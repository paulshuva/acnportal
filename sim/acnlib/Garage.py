import math
import random
from datetime import datetime, timedelta

import config
from acnlib.EV import EV
from acnlib.EVSE import get_EVSE_by_type
from acnlib.SimulationOutput import Event
from acnlib.StatModel import StatModel
from acnlib.TestCase import TestCase


class Garage:
    '''
    The garage class describes the infrastructure of the charging network with
    information about tbe types of the charging stations and the statistical model used
    to generate charging sessions.

    The Garage class is also the owner of the Test Case that the simulator operates on. The Garage class
    can therefore be seen as an intermediate level between the test case and the simulator.
    The Test case can either be created manually from real data and passed to the garage or generated internally
    in the garage by a statistical model.
    '''

    def __init__(self):
        self.EVSEs = []
        self.test_case = None  # TODO(zlee): test_case should live in Simulator
        self.stat_model = StatModel()  # TODO(zlee): this should not be here... not sure where it should live
        self.active_EVs = []
        self.define_garage()
        pass

    def define_garage(self):  # TODO(zlee): this should load in from a file or something similar
        '''
        Creates the EVSEs of the garage.

        :return: None
        '''
        self.EVSEs.append(get_EVSE_by_type('CA-148', 'AeroVironment'))
        self.EVSEs.append(get_EVSE_by_type('CA-149', 'AeroVironment'))
        self.EVSEs.append(get_EVSE_by_type('CA-212', 'AeroVironment'))
        self.EVSEs.append(get_EVSE_by_type('CA-213', 'AeroVironment'))
        for i in range(303, 328):
            # CA-303 to CA-327
            if i >= 320 and i <= 323:
                self.EVSEs.append(get_EVSE_by_type('CA-' + str(i), 'ClipperCreek'))
            else:
                self.EVSEs.append(get_EVSE_by_type('CA-' + str(i), 'AeroVironment'))
        for i in range(489, 513):
            # CA-489 to CA-513
            if i >= 493 and i <= 496:
                self.EVSEs.append(get_EVSE_by_type('CA-' + str(i), 'ClipperCreek'))
            else:
                self.EVSEs.append(get_EVSE_by_type('CA-' + str(i), 'AeroVironment'))

    def update_state(self, pilot_signals, iteration):
        # Checking for forbidden changes in pilot signals
        evse_pilot_signals = {}
        for ev in self.active_EVs:
            new_pilot_signal = pilot_signals[ev.session_id]
            evse_pilot_signals[ev.station_id] = (ev.session_id, new_pilot_signal)
        for evse in self.EVSEs:
            if evse.station_id in evse_pilot_signals:
                session_id = evse_pilot_signals[evse.station_id][0]
                pilot_signal = evse_pilot_signals[evse.station_id][1]
                allowable_rate = evse.change_pilot_signal(pilot_signal, session_id)
                if not allowable_rate:
                    self.submit_event(Event('WARNING',
                                            iteration,
                                            'Wrong increase/decrease of pilot signal for station {0}'.format(
                                                evse.station_id),
                                            session_id))
            else:
                # if no EV is using this station
                evse.last_applied_pilot_signal = 0

        # update the test case
        self.test_case.step(pilot_signals, iteration)

    def submit_event(self, event):
        self.test_case.simulation_output.submit_event(event)

    def event_occurred(self, iteration):
        return self.test_case.event_occurred(iteration)

    def get_simulation_output(self):
        '''
        Returns the simulation output. Also appends the EVSEs used in the simulation
        to the simulation output.

        :return: The simulation output
        :rtype: SimulationOutput
        '''
        simulation_output = self.test_case.get_simulation_output()
        simulation_output.submit_all_EVSEs(self.EVSEs)
        return simulation_output

    def get_actual_charging_rates(self):
        return self.test_case.get_actual_charging_rates()

    def get_active_EVs(self, iteration):
        self.active_EVs = self.test_case.get_active_EVs(iteration)
        return self.active_EVs

    def get_allowable_rates(self, station_id):
        '''
        Returns the allowable pilot level signals for the selected EVSE.
        If no EVSE with the station_id presented is found, it will be created

        :param station_id: (string) The station ID for the EVSE
        :return: (list) List of allowable pilot signal levels for the EVSE
        '''
        evse = next((x for x in self.EVSEs if x.station_id == station_id), None)
        if evse == None:
            # If the EVSE was not found. Create it and add it to available stations
            # default manufacturer is AeroVironment.
            evse = get_EVSE_by_type(station_id, 'AeroVironment')
            self.EVSEs.append(evse)
        return evse.allowable_rates

    @property
    def last_departure(self):
        return self.test_case.last_departure

    @property
    def max_rate(self):
        return self.test_case.max_rate

    @property
    def allowable_rates(self):
        return self.test_case.ALLOWABLE_RATES
