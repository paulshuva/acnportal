'''
This is currently the main starting point of the simulator of the
ACN research portal.
'''

from datetime import datetime

from BaseAlgorithm import *
from acnlib import TestCase
from acnlib.ACNsim import ACNsim
from acnlib.OutputAnalyzer import OutputAnalyzer
from example import acnOptAlgorithm

if __name__ == '__main__':
    test_case = TestCase.generate_test_case_local(
        '/Users/zach401/Documents/Caltech/Research/ACN/Projects/ACN Research Portal/ACN-portal/data/July_25_Sessions.pkl',
        datetime.strptime("02/06/18", "%d/%m/%y"),
        datetime.strptime("09/06/18", "%d/%m/%y"),
        period=1)
    scheduler = MLLF(preemption=False)
    # scheduler = LeastLaxityFirstAlgorithm()
    acnsim = ACNsim()

    simulation_output = acnsim.simulate_real(scheduler, test_case)
    # simulation_output = acnsim.simulate_model(scheduler, period=5, start=datetime.now(), end=(datetime.now() + timedelta(days=7)))

    oa = OutputAnalyzer(simulation_output)
    # oa.plot_station_activity()
    oa.plot_EV_behavioral_stats()
    oa.plot_algorithm_result_stats()
    oa.print_algorithm_result_report()
    oa.plot_EV_daily_arrivals()
    # oa.print_events(type='info')
    # oa.print_station_sessions(test_case)
