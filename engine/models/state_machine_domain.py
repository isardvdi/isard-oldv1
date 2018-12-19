from engine.models.domain_states import DomainStateMachine

sm = DomainStateMachine()

## START AND STOP DOMAINS

sm.define_transition(
    state='Stopped',
    event='Starting',
    action='start_domain_from_id',
    next_states_ok=['Started'],
    next_states_ko=['Failed']
    )

sm.define_transition(
    state='Failed',
    event='Starting',
    action='start_domain_from_id',
    next_states_ok=['Started'],
    next_states_ko=['Failed']
    )

sm.define_transition(
    state='Started',
    event='Stopping',
    action='stop_domain',
    next_states_ok=['Stopped'],
    next_states_ko=['Unknown']
    )

sm.define_transition(
    state='Suspend',
    event='Stopping',
    action='stop_domain',
    next_states_ok=['Stopped'],
    next_states_ko=['Unknown']
    )


sm.define_transition(
    state='Started',
    event='StoppingAndDeleting',
    action='stop_domain_and_delete',
    next_states_ok=['Stopped'],
    next_states_ko=['Unknown']
    )

## DISPOSABLES

sm.define_transition(
    state='Started',
    event='StoppingAndDeleting',
    action='stop_domain_and_delete',
    next_states_ok=['Stopped'],
    next_states_ko=['Unknown']
    )

sm.define_transition(
    state='Suspended',
    event='StoppingAndDeleting',
    action='stop_domain_and_delete',
    next_states_ok=['Stopped'],
    next_states_ko=['Unknown']
    )

## UPDATE DOMAINS

sm.define_transition(
    state='Stopped',
    event='Updating',
    action='updating_from_create_dict',
    next_states_ok=['Stopped'],
    next_states_ko=['Failed']
    )

sm.define_transition(
    state='Downloaded',
    event='Updating',
    action='updating_from_create_dict',
    next_states_ok=['Stopped'],
    next_states_ko=['Failed']
    )

sm.define_transition(
    state='Failed',
    event='Updating',
    action='updating_from_create_dict',
    next_states_ok=['Stopped'],
    next_states_ko=['Failed']
    )

# DELETE DOMAINS
sm.define_transition(
    state='Stopped',
    event='Deleting',
    action='deleting_disks_from_domain',
    next_states_ok=['Stopped'],
    next_states_ko=['Failed']
    )


