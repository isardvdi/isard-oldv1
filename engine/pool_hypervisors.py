# Copyright 2017 the Isard-vdi project authors:
#      Alberto Larraz Dalmases
#      Josep Maria Viñolas Auquer
# License: AGPLv3

# coding=utf-8

from datetime import datetime, timedelta


from .hyp import hyp
from .log import *
from .db import get_hyp_hostnames, update_hyp_status, update_db_hyp_info
# from ui_actions import UiActions
from .db import get_domain
from .db import get_hyp_hostnames_online, initialize_db_status_hyps
#from threads import launch_threads_status_hyp, launch_thread_worker, launch_disk_operations_thread
#from threads import dict_threads_active
from .events_recolector import launch_thread_hyps_event
from .functions import try_ssh


import threading
# from ..hyp_threads import launch_all_hyps_threads

from .db import get_hypers_in_pool
from .config import CONFIG_DICT

TIMEOUT_TRYING_SSH = float(CONFIG_DICT["TIMEOUTS"]["timeout_trying_ssh"])


class PoolHypervisors():
    def __init__(self,id_pool):
        self.id_pool = id_pool


        self.last_index=0
    def get_next(self,to_create_disk=False, path_selected='', dict_domain=None, action='start'):
        # NEXT RELEASES WE WILL WORK HERE
        # INFO TO DEVELOPER, SI se crea un disco podemos decidir algo distinto... en la decision de pools...
        self.hyps = get_hypers_in_pool(self.id_pool)
        self.total_hyps = len(self.hyps)



        if self.total_hyps > 0:
            if to_create_disk is False:
                if self.last_index >= self.total_hyps-1:
                    self.last_index = 0
                else:
                    self.last_index += 1
                hyp_selected = self.hyps[self.last_index]
                if action == 'start':
                    pools_stats.update_domain_in_hyp_as_started(hyp_selected, dict_domain['id'], dict_domain)
                elif action == 'stop':
                    pools_stats.update_domain_in_hyp_as_stopped(hyp_selected, dict_domain['id'], dict_domain)
                return hyp_selected
            elif to_create_disk is True and len(path_selected) > 0:
                pass

        else:
            return False

class hyp_parameters(object):
    def __init__(self,hyp_id,list_parameters,average_interval_in_seconds=300.0):
        self.average_interval = timedelta(seconds=average_interval_in_seconds)

        self.hyp_id = hyp_id
        self.timestamps = []
        self.last_timestamp = None
        self.last_diff = None
        self.parameters = {}
        self.create_parameters(list_parameters)

    def create_parameters(self,list_parameters):
        for parameter in list_parameters:
            self.parameters[parameter] = {}
            self.parameters[parameter]['current_value'] = None
            self.parameters[parameter]['max_value'] = None
            self.parameters[parameter]['min_value'] = None
            self.parameters[parameter]['average_value'] = None
            self.parameters[parameter]['values'] = []

    def add_values(self,d_values,timestamp=None):

        if timestamp is None:
            self.last_timestamp = datetime.now()
        elif type(timestamp) is not datetime:
            log.error('Timestamp format must be dateime when inserting value in hypervisor parameter class, timestamp will be now')
            self.last_timestamp = datetime.now()
        else:
            self.last_timestamp = timestamp

        self.purgue_values()

        for parameter in self.parameters.keys():
            if parameter not in d_values.keys():
                current_value = None
            else:
                try:
                    current_value = float(d_values[parameter])
                except ValueError:
                    log.error('ValueError: {} when adding value in hypervisor parameter {}'.format(d_values[parameter], self.hyp_id))
                    current_value = None
                except TypeError:
                    log.error(
                        'TypeError: {} when adding value in hypervisor parameter {}'.format(str(type(d_values[parameter])), self.hyp_id))
                    current_value = None

            self.parameters[parameter]['values'].append(current_value)

        self.update_stats()

    def update_stats(self):
        for parameter in self.parameters.keys():
            l = [a for a in self.parameters[parameter]['values']  if a is not None]
            if len(l) > 0:
                self.parameters[parameter]['current_value'] = l[-1]
                self.parameters[parameter]['max_value'] = max(l)
                self.parameters[parameter]['min_value'] = min(l)
                self.parameters[parameter]['average_value'] = sum(l)/len(l)
            else:
                self.parameters[parameter]['current_value'] = None
                self.parameters[parameter]['max_value'] = None
                self.parameters[parameter]['min_value'] = None
                self.parameters[parameter]['average_value'] = None

                #examples with numpy
                # x = np.random.rand(1000) * 10
                # a = np.asarray(x)
                # #lower than 1 convert to
                # low = a < 1
                # a[low] = 1
                #
                #
                # #high values > 5 =>  10
                # high = a > 5
                # a[high] = a[high] * 2

    def update_domain_as_started(self,domain_id,domain_dict = None):
        if domain_dict is None:
            domain_dict = get_domain(domain_id)
        if domain_dict is not None:
            self.parameters['free_mem_for_domains']['values'][-1] -= domain_dict['hardware']['currentMemory']
            self.parameters['total_domains']['values'][-1] += 1
            self.parameters['vcpus']['values'][-1] += domain_dict['hardware']['vcpus']
            self.parameters['rate_vcpus_rcpus']['values'][-1] = self.parameters['vcpus']['values'][-1] / self.parameters['total_threads_cpu']['values'][-1]
            self.parameters['rate_free_mem_for_domains']['values'][-1] = self.parameters['free_mem_for_domains']['values'][-1] / self.parameters['total_memory']['values'][-1]

            self.update_stats()

    def update_domain_as_stopped(self,domain_id,domain_dict = None):
        if domain_dict is None:
            domain_dict = get_domain(domain_id)
        if domain_dict is not None:
            self.parameters['free_mem_for_domains']['values'][-1] += domain_dict['hardware']['currentMemory']
            self.parameters['total_domains']['values'][-1] -= 1
            self.parameters['vcpus']['values'][-1] -= domain_dict['hardware']['vcpus']
            self.parameters['rate_vcpus_rcpus']['values'][-1] = self.parameters['vcpus']['values'][-1] / self.parameters['total_threads_cpu']['values'][-1]
            self.parameters['rate_free_mem_for_domains']['values'][-1] = self.parameters['free_mem_for_domains']['values'][-1] / self.parameters['total_memory']['values'][-1]

            self.update_stats()

    def purgue_values(self):

            # remove_items_from = 0
            for old_time in self.timestamps.copy():
                if self.last_timestamp - old_time > self.average_interval or self.last_timestamp < old_time:
                    self.timestamps.pop(0)
                    for parameter in self.parameters.keys():
                        assert len(self.parameters[parameter]['values']) == len(self.timestamps) + 1
                        self.parameters[parameter]['values'].pop(0)
                else:
                    break
                # remove_items_from += 1


            self.timestamps.append(self.last_timestamp)






class HypStats(object):
    def __init__(self,id_pool,weights):
        self.id_pool = id_pool
        self.lock = threading.Lock()
        self.config_parameters = {
            'cpu_freq':{},
            'cpu_idle':{},
            'cpu_iowait':{},
            'vcpus':{},
            'total_memory':{},
            'total_threads_cpu':{},
            'total_domains':{},
            'free_mem_for_domains': {},
            'rate_free_mem_for_domains': {},
            'rate_vcpus_rcpus': {},
            'rate_ballon_disposable': {}
        }
        self.hyp_stats = {}
        self.pool_weights = weights
        self.average_time = 60

    def update_domain_in_hyp_as_started(self,id_hyp,domain_id,domain_dict=None):
        if id_hyp in self.hyp_stats.keys():
            self.lock.acquire()
            self.hyp_stats[id_hyp].update_domain_as_started(domain_id,domain_dict)
            self.lock.release()
        else:
            log.error('Hypervisor {} try to insert stats in stats from hyp and not exist in hyp_stats dictionary'.format(id_hyp))

    def update_domain_in_hyp_as_stopped(self,id_hyp,domain_id,domain_dict=None):
        if id_hyp in self.hyp_stats.keys():
            self.lock.acquire()
            self.hyp_stats[id_hyp].update_domain_as_stopped(domain_id,domain_dict)
            self.lock.release()
        else:
            log.error('Hypervisor {} try to insert stats in stats from hyp and not exist in hyp_stats dictionary'.format(id_hyp))

    def new_stats_hyp(self,id_hyp, d_values):
        if id_hyp in self.hyp_stats.keys():
            self.lock.acquire()
            self.hyp_stats[id_hyp].add_values(d_values, timestamp=None)
            self.lock.release()
        else:
            log.error('Hypervisor {} try to insert stats in stats from hyp and not exist in hyp_stats dictionary'.format(id_hyp))

    def add_hyp(self,id_hyp):
        self.lock.acquire()
        self.hyp_stats[id_hyp] = hyp_parameters(list_parameters=self.config_parameters.keys(),
                                                average_interval_in_seconds= self.average_time,
                                                hyp_id = id_hyp)
        self.lock.release()

    def remove_hyp(self,id_hyp):
        self.lock.acquire()
        self.hyp_stats.pop(id_hyp)
        self.lock.release()

    def calculate_scores(self,domain_mem,domain_vcpus):
        pass
        #para todos los hyper mirar si free_mem > domain_mem

        #a partir de self.pool_wights
        #pillar el peso, el tipo de dato y guardar el valor y e calcular el score
        # self.matrix_scores[parameter][hyp_id][value]
        # self.matrix_scores[parameter][hyp_id][score]

    #sumar todoslos scores y guardar las puntuaciones de cada hyper
    #self.list_selected_hyps => pila con los últimos hyps seleccionados, puntuación y domain que arrancaron
    #devolver el que tiene más puntuación para arrancar



    def increment(self):
        logging.debug('Waiting for a lock')
        self.lock.acquire()
        try:
            logging.debug('Acquired a lock')
            self.value = self.value + 1
        finally:
            logging.debug('Released a lock')
            self.lock.release()


from engine.db import get_hypers_in_pool


weights=[{'avg_cpu_idle':{'parameter':'cpu_idle',
                          'weight':100,
                          'type':'avg'}
          },
         {'free_memory':{'parameter':'free_mem_for_domains',
                          'weight':20,
                          'type':'last'}
          },
         {'cpu_freq':   {'parameter':'cpu_freq',
                          'weight':10,
                          'type':'constant'}
          },
         {'io_wait_peaks':   {'parameter':'cpu_iowait',
                          'weight':-50,
                          'type':'max'}
          }
        ]


pools_stats = dict()
pools_stats['default'] = HypStats('default',weights)

for hyp_id in get_hypers_in_pool('default'):
    pools_stats['default'].add_hyp(hyp_id)