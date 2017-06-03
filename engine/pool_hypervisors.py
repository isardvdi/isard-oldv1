# Copyright 2017 the Isard-vdi project authors:
#      Alberto Larraz Dalmases
#      Josep Maria Viñolas Auquer
# License: AGPLv3

# coding=utf-8

from datetime import datetime, timedelta
from pprint import pprint,pformat
from random import random

from .hyp import hyp
from .log import *
from .db import get_hyp_hostnames, update_hyp_status, update_db_hyp_info
# from ui_actions import UiActions
from .db import get_domain, get_weights_config, get_weight_profile_for_pool
from .db import get_hypers_in_pool
from .db import get_hyp_hostnames_online, initialize_db_status_hyps
#from threads import launch_threads_status_hyp, launch_thread_worker, launch_disk_operations_thread
#from threads import dict_threads_active
from .events_recolector import launch_thread_hyps_event
from .functions import normalize_parameter


import threading
# from ..hyp_threads import launch_all_hyps_threads

from .db import get_hypers_in_pool
from .config import CONFIG_DICT

TIMEOUT_TRYING_SSH = float(CONFIG_DICT["TIMEOUTS"]["timeout_trying_ssh"])



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
            self.parameters[parameter]['current'] = None
            self.parameters[parameter]['max'] = None
            self.parameters[parameter]['min'] = None
            self.parameters[parameter]['average'] = None
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
                    log.error('ValueError: when adding value for parameter {} in hypervisor {}'.format(parameter, self.hyp_id))
                    current_value = None
                except TypeError:
                    log.error(
                        'TypeError: type must be number and type is {} when adding value in hypervisor parameter {}'.format(str(type(d_values[parameter])), self.hyp_id))
                    current_value = None

            self.parameters[parameter]['values'].append(current_value)

        self.update_stats()

    def update_stats(self):
        for parameter in self.parameters.keys():
            l = [a for a in self.parameters[parameter]['values']  if a is not None]
            if len(l) > 0:
                self.parameters[parameter]['current'] = l[-1]
                self.parameters[parameter]['max'] = max(l)
                self.parameters[parameter]['min'] = min(l)
                self.parameters[parameter]['average'] = sum(l)/len(l)
            else:
                self.parameters[parameter]['current'] = None
                self.parameters[parameter]['max'] = None
                self.parameters[parameter]['min'] = None
                self.parameters[parameter]['average'] = None

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
            self.parameters['random']['values'][-1] = random()
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
            self.parameters['random']['values'][-1] = random()
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
    def __init__(self,id_pool,d_weights_config):
        self.id_pool = id_pool
        self.lock = threading.Lock()
        self.config_parameters = {
            'cpu_freq':{},
            'cpu_idle':{},
            'cpu_iowait':{},
            'random':{},
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
        # self.pool_weights = weights
        self.average_time = 60
        self.d_weights_config = d_weights_config

    def get_hyps_with_free_mem(self,domain_memory):
        domain_memory = domain_memory / (1024*1024.0)
        hyps_to_choose = []

        for hyp_id in self.hyp_stats.keys():
            free_memory = self.hyp_stats[hyp_id].parameters['free_mem_for_domains']['values'][-1]
            if free_memory >= domain_memory:
                hyps_to_choose.append(hyp_id)

        return hyps_to_choose

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

    def calculate_scores(self,hyps_to_choose):
        d_scores = dict()
        score_selected = None
        hyp_selected = None
        self.pool_weights = get_weight_profile_for_pool(self.id_pool )

        for hyp_id in hyps_to_choose:
            d_scores[hyp_id] = dict()
            d_scores[hyp_id]['score'] = 0
            d_scores[hyp_id]['selected'] = False
            d_scores[hyp_id]['by_parameters'] = dict()

            pprint(self.hyp_stats[hyp_id].parameters)

            for key,d_weight in self.pool_weights.items():

                parameter = d_weight['parameter']
                d_scores[hyp_id]['by_parameters'][key] = dict()
                type = d_weight['type']
                weight = d_weight['weight']
                value = self.hyp_stats[hyp_id].parameters[parameter][type]

                normalized = normalize_parameter(value,d_weights_config[parameter])
                score_parameter = normalized * weight

                d_scores[hyp_id]['by_parameters'][key]['parameter'] = key
                d_scores[hyp_id]['by_parameters'][key]['score'] = score_parameter
                d_scores[hyp_id]['by_parameters'][key]['value'] = value
                d_scores[hyp_id]['by_parameters'][key]['normalized'] = normalized
                d_scores[hyp_id]['by_parameters'][key]['weight'] = weight
                d_scores[hyp_id]['by_parameters'][key]['type'] = type
                d_scores[hyp_id]['score'] += score_parameter

            if score_selected is None:
                score_selected = d_scores[hyp_id]['score']
                hyp_selected = hyp_id
            elif d_scores[hyp_id]['score'] > score_selected:
                score_selected = d_scores[hyp_id]['score']
                hyp_selected = hyp_id

        d_scores[hyp_selected]['selected'] = True
        return hyp_selected,d_scores


    def increment(self):
        logging.debug('Waiting for a lock')
        self.lock.acquire()
        try:
            logging.debug('Acquired a lock')
            self.value = self.value + 1
        finally:
            logging.debug('Released a lock')
            self.lock.release()





# weights={'avg_cpu_idle':{'parameter':'cpu_idle',
#                           'weight':100,
#                           'type':'average'}
#           ,
#          'free_memory':{'parameter':'free_mem_for_domains',
#                           'weight':20,
#                           'type':'current'}
#           ,
#          'cpu_freq':   {'parameter':'cpu_freq',
#                           'weight':10,
#                           'type':'current'}
#           ,
#          'io_wait_peaks':   {'parameter':'cpu_iowait',
#                           'weight':-50,
#                           'type':'max'}
#
#           }


d_weights_config = get_weights_config()
pools_stats = dict()
pools_stats['default'] = HypStats('default',d_weights_config)

for hyp_id in get_hypers_in_pool('default'):
    pools_stats['default'].add_hyp(hyp_id)


class PoolHypervisors():
    def __init__(self, id_pool):
        self.id_pool = id_pool

        self.last_index = 0

    def calculate_weights(self,hyps_to_choose):
        global pools_stats


    def get_next(self, to_create_disk=False, path_selected='', dict_domain=None, action='start', verify_free_mem=True):
        # NEXT RELEASES WE WILL WORK HERE
        # INFO TO DEVELOPER, SI se crea un disco podemos decidir algo distinto... en la decision de pools...
        self.hyps = get_hypers_in_pool(self.id_pool)
        self.total_hyps = len(self.hyps)


        global pools_stats

        if type(dict_domain) is dict:
            # VERIFY IF HYPERVISOR HAVE FREE MEMORY
            if verify_free_mem is True:
                if self.id_pool in pools_stats.keys():
                    hyps_to_choose = pools_stats[self.id_pool].get_hyps_with_free_mem(dict_domain['hardware']['memory'])
                    if len(hyps_to_choose) == 0:
                        log.error('pool {} have not hypervisor with free ram'.format(self.id_pool))
                        reason= 'domain not start because pool {} have not hypervisor with free ram'.format(self.id_pool)
                        return False,reason
                else:
                    log.error('pool {} does not exist when trying to get next hypervisor'.format(self.id_pool))
                    return False
            else:
                hyps_to_choose =  self.hyps

            if len(hyps_to_choose) == 0:
                log.error('pool {} have not hypervisor enable or available'.format(self.id_pool))
                reason = 'domain not start because pool {} have not hypervisor enable or available'.format(self.id_pool)
                return False, reason

            #FORCE HYPERVISOR SELECTED IN DOMAIN

            if 'force_hypervisor' in dict_domain:
                if dict_domain['force_hypervisor'] is str:
                    if len(dict_domain['force_hypervisor']) > 0:
                        if dict_domain['force_hypervisor'] in hyps_to_choose:
                            reason = 'hypervisor forced in domain available'
                            log.info('hypervisor {} selected to start domain: {} - reason: {}'.format(dict_domain['force_hypervisor'],
                                                                                                      dict_domain['id'],
                                                                                                      reason))

                            return dict_domain['force_hypervisor'],reason
                        else:
                            reason = 'hypervisor forced in domain not available'
                            log.info('hypervisor {} selected to start domain: {} - reason: {}'.format(
                                    dict_domain['force_hypervisor'],
                                    dict_domain['id'],
                                    reason))
                            return False,reason

            if len(hyps_to_choose) == 1:
                hyp_selected = hyps_to_choose[0]
                reason = 'only one hypervisor available, no weights calculated'
                log.info('hypervisor {} selected to start domain: {} - reason: {}'.format(hyp_selected,
                                                                                   dict_domain['id'],
                                                                                   reason))
                return hyp_selected, reason

            if len(hyps_to_choose) >= 1:

                hyp_selected,d_scores = pools_stats[self.id_pool].calculate_scores(hyps_to_choose)
                reason = 'hypervisor with more score when calculate weights'

                log.info('hypervisor {} selected to start domain: {} - reason: {}'.format(hyp_selected,
                                                                                   dict_domain['id'],
                                                                                   reason))
                #TODO A MODO DEBUG
                log.info('DICTIONARY of score decision with parameters, values and weights:')
                log.info(pformat(d_scores))

                return hyp_selected, reason
                

