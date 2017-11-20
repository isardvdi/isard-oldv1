import queue
import threading
import time

from engine.models.hyp import hyp
from engine.services.db import get_hyp_hostname_from_id, update_db_hyp_info, update_domain_status, update_hyp_status, \
    update_domains_started_in_hyp_to_unknown
from engine.services.lib.functions import get_tid
from engine.services.log import log
from engine.services.threads.threads import TIMEOUT_QUEUES, launch_action_disk, RETRIES_HYP_IS_ALIVE, \
    TIMEOUT_BETWEEN_RETRIES_HYP_IS_ALIVE


class HypWorkerThread(threading.Thread):
    def __init__(self, name, hyp_id, queue_actions, queue_master=None):
        threading.Thread.__init__(self)
        self.name = name
        self.hyp_id = hyp_id
        self.stop = False
        self.queue_actions = queue_actions
        self.queue_master = queue_master

    def run(self):
        self.tid = get_tid()
        log.info('starting thread: {} (TID {})'.format(self.name, self.tid))
        host, port, user = get_hyp_hostname_from_id(self.hyp_id)
        port = int(port)
        self.hostname = host
        self.h = hyp(self.hostname, user=user, port=port)
        self.h.get_hyp_info()
        update_db_hyp_info(self.hyp_id, self.h.info)
        hyp_id = self.hyp_id

        while self.stop is not True:
            try:
                # do={type:'start_domain','xml':'xml','id_domain'='prova'}
                action = self.queue_actions.get(timeout=TIMEOUT_QUEUES)

                log.debug('recibe {}'.format(action['type']))

                if action['type'] == 'start_paused_domain':
                    log.debug('xml to start some lines...: {}'.format(action['xml'][30:100]))
                    try:
                        self.h.conn.createXML(action['xml'], flags=VIR_DOMAIN_START_PAUSED)
                        # 32 is the constant for domains paused
                        # reference: https://libvirt.org/html/libvirt-libvirt-domain.html#VIR_CONNECT_LIST_DOMAINS_PAUSED
                        FLAG_LIST_DOMAINS_PAUSED = 32
                        if len([d for d in self.h.conn.listAllDomains(FLAG_LIST_DOMAINS_PAUSED) if
                                d.name() == action['id_domain']]) == 1:
                            # domain started in pause mode
                            domain = [d for d in self.h.conn.listAllDomains(FLAG_LIST_DOMAINS_PAUSED) if
                                      d.name() == action['id_domain']][0]
                            if domain.destroy() == 0:
                                # domain is destroyed, all ok
                                update_domain_status('Stopped', action['id_domain'], hyp_id='',
                                                     detail='Domain is stopped in hyp{}'.format(self.hyp_id))
                                log.debug(
                                    'domain {} creating operation finalished. Started paused and destroyed in hypervisor {}. Now status is Stopped. READY TO USE'.format(
                                        action['id_domain'], self.hyp_id))

                                if action['id_domain'].find('_disposable_') == 0:
                                    update_domain_status('Starting', action['id_domain'],
                                                         detail='Disposable domain starting')
                            else:
                                update_domain_status('Crashed', action['id_domain'], hyp_id=self.hyp_id,
                                                     detail='Domain is created, started in pause mode but not destroyed,creating domain operation is aborted')
                                log.error(
                                    'domain {} started paused but not destroyed in hypervisor {}, must be destroyed'.format(
                                        action['id_domain'], self.hyp_id))
                        else:
                            update_domain_status('Crashed', action['id_domain'], hyp_id=self.hyp_id,
                                                 detail='XML for domain {} can not start in pause mode in hypervisor {}, creating domain operation is aborted by unknown cause'.format(
                                                     action['id_domain'], self.hyp_id))
                            log.error(
                                'XML for domain {} can not start in pause mode in hypervisor {}, creating domain operation is aborted, not exception, rare case, unknown cause'.format(
                                    action['id_domain'], self.hyp_id))

                    except libvirtError as e:
                        from pprint import pformat
                        error_msg = pformat(e.get_error_message())

                        update_domain_status('FailedCreatingDomain', action['id_domain'], hyp_id=self.hyp_id,
                                             detail='domain {} failed when try to start in pause mode in hypervisor {}. creating domain operation is aborted')
                        log.error(
                            'Exception in libvirt starting paused xml for domain {} in hypervisor {}. Exception message: {} '.format(
                                action['id_domain'], self.hyp_id, error_msg))
                    except Exception as e:
                        update_domain_status('Crashed', action['id_domain'], hyp_id=self.hyp_id,
                                             detail='domain {} failed when try to start in pause mode in hypervisor {}. creating domain operation is aborted')
                        log.error(
                            'Exception starting paused xml for domain {} in hypervisor {}. NOT LIBVIRT EXCEPTION, RARE CASE. Exception message: '.format(
                                str(e)))

                ## START DOMAIN
                elif action['type'] == 'start_domain':
                    log.debug('xml to start some lines...: {}'.format(action['xml'][30:100]))
                    try:
                        self.h.conn.createXML(action['xml'])
                        update_domain_status('Started', action['id_domain'], hyp_id=self.hyp_id, detail='')
                        log.debug('STARTED domain {}: createdXML action in hypervisor {} has been sent'.format(
                            action['id_domain'], host))
                    except Exception as e:
                        update_domain_status('Failed', action['id_domain'], hyp_id=self.hyp_id, detail=str(e))
                        log.debug('exception in starting domain {}: '.format(e))

                ## STOP DOMAIN
                elif action['type'] == 'stop_domain':
                    log.debug('action stop domain: {}'.format(action['id_domain'][30:100]))
                    try:
                        self.h.conn.lookupByName(action['id_domain']).destroy()
                        update_domain_status('Stopped', action['id_domain'], hyp_id='')
                        log.debug('STOPPED domain {}'.format(action['id_domain']))
                    except Exception as e:
                        update_domain_status('Failed', action['id_domain'], hyp_id=self.hyp_id, detail=str(e))
                        log.debug('exception in stopping domain {}: '.format(e))

                elif action['type'] in ['create_disk', 'delete_disk']:
                    launch_action_disk(action,
                                       self.hostname,
                                       user,
                                       port)

                    # ## DESTROY THREAD
                    # elif action['type'] == 'destroy_thread':
                    #     list_works_in_queue = list(self.queue_actions.queue)
                    #     if self.queue_master is not None:
                    #         self.queue_master.put(['destroy_working_thread',self.hyp_id,list_works_in_queue])
                    #     #INFO TO DEVELOPER, si entra aquí es porque no quedaba nada en cola, si no ya lo habrán matado antes
                    #
                    #     log.error('thread worker from hypervisor {} exit from error status'.format(hyp_id))
                    #

                    # raise 'destoyed'

                elif action['type'] == 'create_disk':

                    pass


                elif action['type'] == 'hyp_info':
                    self.h.get_hyp_info()
                    log.debug('hypervisor motherboard: {}'.format(self.h.info['motherboard_manufacturer']))

                ## DESTROY THREAD
                elif action['type'] == 'stop_thread':
                    self.stop = True
                else:
                    log.error('type action {} not supported in queue actions'.format(action['type']))
                    # time.sleep(0.1)
                    ## TRY DOMAIN


            except queue.Empty:
                try:
                    self.h.conn.getLibVersion()
                    pass
                    # log.debug('hypervisor {} is alive'.format(host))
                except:
                    log.info('trying to reconnect hypervisor {}, alive test in working thread failed'.format(host))
                    alive = False
                    for i in range(RETRIES_HYP_IS_ALIVE):
                        try:
                            time.sleep(TIMEOUT_BETWEEN_RETRIES_HYP_IS_ALIVE)
                            self.h.conn.getLibVersion()
                            alive = True
                            log.info('hypervisor {} is alive'.format(host))
                            break
                        except:
                            log.info('hypervisor {} is NOT alive'.format(host))
                    if alive is False:
                        try:
                            self.h.connect_to_hyp()
                            self.h.conn.getLibVersion()
                        except:
                            log.debug('hypervisor {} failed'.format(host))
                            log.error('fail reconnecting to hypervisor {} in working thread'.format(host))
                            reason = self.h.fail_connected_reason
                            update_hyp_status(self.hyp_id, 'Error', reason)
                            update_domains_started_in_hyp_to_unknown(self.hyp_id)

                            list_works_in_queue = list(self.queue_actions.queue)
                            if self.queue_master is not None:
                                self.queue_master.put(['error_working_thread', self.hyp_id, list_works_in_queue])
                            log.error('thread worker from hypervisor {} exit from error status'.format(hyp_id))
                            self.active = False
                            break