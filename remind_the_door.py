import appdaemon.plugins.hass.hassapi as hass

import json


def allowance(entity, interested_state='on'):
    '''For how long (in seconds) the door can be kept open or close.
    '''
    door_on_allowance = {
        'binary_sensor.wyzesense_freezer':10,
        'binary_sensor.wyzesense_fridge':10,
    }

    door_off_allowance = {}

    if interested_state=='on':
        return door_on_allowance.get(entity, 10)

    return door_off_allowance.get(entity, 10)

class Remind_the_door(hass.Hass):

    def initialize(self):

        self.door_dict = [
            'binary_sensor.wyzesense_freezer',
            'binary_sensor.wyzesense_fridge',
        ]

        # listen_state
        for door in self.door_dict:
            self.get_entity(door).listen_state(
                self.tracker,
            )

        # A dict of timer.
        self.timer_dict = {}  # ?

    def tracker(self, entity, attribute, old, new, kwargs):

        # Cancel timer when the door is closed.
        if new == 'off':
            try:
                self.cancel_timer(self.timer_dict[entity])
                self.log(f'canceled timer {entity}')
            except Exception as e:
                self.log(f'Failed to cancel timer. {e}')

        # Create timer and notify.
        if new == 'on':

            self.timer_dict[entity] = self.run_in(
                self.notifier, 
                delay=allowance(entity),
                entity_name=entity  # as reference in notifier
        )

        self.log(json.dumps(self.timer_dict))

    def notifier(self, kwargs):

        # Get friendly name.
        friendly_name = self.get_state(
            kwargs['entity_name'],
            attribute='friendly_name'
        )

        self.call_service(
            'notify/send_email_to_rick_notifier',
            message='',
            title = f'{friendly_name} left open',
        )
        
        self.call_service(
            'tts/google_translate_say',
            entity_id='media_player.dummy',
            message=f'I am cool.'
        )
