# Copyright 2018 the Isard-vdi project authors:
#      Alberto Larraz Dalmases
#      Josep Maria Viñolas Auquer
# License: AGPLv3

# Manage domains state

# coding=utf-8

from pprint import pprint


class DomainStateMachine():
    def __init__(self):
        self.l_states = []
        self.l_events = []
        self.l_ui_actions = []
        self.l_transitions = []
        self.define_states()
        self.define_events()
        self.define_ui_actions()
        self.events = self.Events()
        self.states = self.States()
        self.actions = self.Actions()


    def define_states(self):
        self.l_states = set([
            'New',
            'DiskCreated',
            'Deleted',

            'Stopped',
            'Started',
            'Paused',

            'Failed',
            'FailedCreatingDomain',
            'Unknown',
            'Crashed',

            'DiskDeleted',

            'TemplateDiskCreated',
            'Downloaded',
            'Disabled',
            ])

    def define_events(self):
        self.l_events = set([
            'Starting',
            'Stopping',
            'Pausing',
            'StartingDomainDisposable',

            'CreatingAndStarting',
            'StoppingAndDeleting',

            'Updating',
            'Deleting',
            'DeletingDomainDisk',

            'CreatingDomain',
            'CreatingDisk',
            'CreatingTemplateDisk',
            'CreatingDiskFromScratch',
            'CreatingDomainFromBuilder',
            'CreatingFromBuilder',
            'CreatingTemplate',

            'RunningVirtBuilder',
            ])

    def define_ui_actions(self):
        self.l_ui_actions = set([
            'action_from_api',
            'create_template_disks_from_domain',
            'create_template_in_db',
            'creating_and_test_xml_start',
            'creating_disk_from_scratch',
            'creating_disk_from_virtbuilder',
            'creating_disks_from_template',
            'creating_test_disk',
            'delete_domain',
            'delete_ferrary',
            'delete_template',
            'deleting_disks_from_domain',
            'destroy_domain_from_id',
            'domain_from_template',
            'ferrary_from_domain',
            'start_domain_from_id',
            'start_domain_from_xml',
            'start_ferrary',
            'start_paused_domain_from_xml',
            'stop_domain',
            'stop_domain_from_id',
            'stop_ferrary',
            'update_domain',
            'update_template',
            'updating_from_create_dict',
            ])


    def define_transition(self,state,event,action,next_states_ok, next_states_ko):
        if type(next_states_ok) is str:
            next_states_ok = [next_states_ok]
        if type(next_states_ko) is str:
            next_states_ko = [next_states_ko]
        next_states_ok = set(next_states_ok)
        next_states_ko = set(next_states_ko)

        if state not in self.l_states:
            print('state not valid')
            return False
        if event not in self.l_events:
            print('event not valid')
            return False
        if action not in self.l_ui_actions:
            print('action not valid')
            return False
        if next_states_ok.issubset(self.l_states) is False:
            print('next states are invalid')
            return False
        if next_states_ko.issubset(self.l_states) is False:
            print('next states ko are invalid')
            return False

        #only one state - event => action
        l_transition = [state,event,action,next_states_ok, next_states_ko]
        if l_transition[:1] not in [l[:2] for l in self.l_transitions]:
            print(f'--NEW TRANSITION-- \nstate: {state} \nevent: {event} \naction: {action}\n')
            self.l_transitions.append(l_transition)
            self.events.add_event(event,action,state)
            self.states.add_state(state,event,action,next_states_ok, next_states_ko)
            self.actions.add_action(state,event,action,next_states_ok, next_states_ko)


    class Events:
        def __init__(self):
            self.d = {}
            pass
        def add_event(self,event,action,state):
            from_state = state
            d={from_state:action}
            if event not in dir(self):
                setattr(self,event,d)
                self.d[event] = self.__getattribute__(event)
            else:
                self.__getattribute__(event)[from_state] = action


    class Actions:
        def __init__(self):
            self.d={}
            pass
        def add_action(self,state,event,action,next_states_ok, next_states_ko):
            d_new = {
                'from_events':set(),
                'from_states':set(),
            }
            if action not in dir(self):
                setattr(self,action,d_new.copy())
            d = self.__getattribute__(action)
            self.d[action] = d
            d['from_events'].add(event)
            d['from_states'].add(state)

    class States:
        def __init__(self):
            self.d = {}
            pass
        def add_state(self,state,event,action,next_states_ok, next_states_ko):
            d_new={'next_states':set(),
               'next_states_ok':set(),
               'next_states_ko':set(),
               'events':set(),
               'prev_states':set(),
               'prev_events':set()

            }
            if state not in dir(self):
                setattr(self,state,d_new.copy())

            d = self.__getattribute__(state)
            self.d[state] = d
            [d['next_states'].add(s) for s in next_states_ok]
            [d['next_states'].add(s) for s in next_states_ko]
            [d['next_states_ok'].add(s) for s in next_states_ok]
            [d['next_states_ko'].add(s) for s in next_states_ko]
            d['events'].add(event)
            for s in next_states_ok:
                if s not in dir(self):
                    setattr(self, s, d_new.copy())
                d = self.__getattribute__(s)
                self.d[s] = d
                d['prev_events'].add(event)
                d['prev_states'].add(state)














