import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from __init__ import power_to_energy_conversion_ratio, time_resolution
# from ortools.constraint_solver import routing_enums_pb2
# from ortools.constraint_solver import pywrapcp
from ortools.linear_solver import pywraplp

def find_duration_of_charging_in_minutes(P_in, time_resolution_is):
    time_slots = pd.date_range("00:00", periods=len(P_in), freq= str(time_resolution_is) + "min")
    df = pd.DataFrame({ 'P_in': P_in, 'timestamp':time_slots })
    df = df.set_index(['timestamp'])
    last_charge = df[df['P_in'] != 0.0].index[-1]
    duration = last_charge.hour * 60 + last_charge.minute + 15
    # import ipdb; ipdb.set_trace()
    return duration

def run_opt_1st(EV_testing, market_prices, max_number_of_intervals:int= 20, final_SoC:float = 1.0): # 
    """
    1st: cost-optimal (time is indifferent) option. 
    + an upper limit for time constraint (maximum number of time intervals, e.g for 5 hours - > 5 x 4 = 20 .)
    + desired final SoC is an additional input (default is 100% - > 1.0) 

    """
    solver = pywraplp.Solver.CreateSolver('GLOP')

    E_ss_t = [solver.NumVar(0.0, solver.infinity(), 'E_ess_'+ str(i) ) for i in range(max_number_of_intervals)]
    P_ess_in_t = [solver.NumVar(0.0, solver.infinity(), 'P_ess_in_'+ str(i) ) for i in range(max_number_of_intervals)]
    # P_ess_out_t = [solver.NumVar(0.0, solver.infinity(), 'P_ess_out_'+ str(i) ) for i in range(max_number_of_intervals)]

    print('Number of variables =', solver.NumVariables())

    for i in range(max_number_of_intervals):
        solver.Add(P_ess_in_t[i] <= EV_testing.P_max ) # + P_ess_out_t[i]
        if i != 0:
            solver.Add(solver.Sum([power_to_energy_conversion_ratio * P_ess_in_t[j] * EV_testing.hetta_in for j in range(i)])  + EV_testing.E_ss_0 == E_ss_t[i] ) # - solver.Sum([P_ess_out_t[j] * EV_testing.hetta_out for j in range(i)])
        else:
            solver.Add(E_ss_t[i] == EV_testing.E_ss_0)
        solver.Add(E_ss_t[i] <= EV_testing.E_max_capacity)
        solver.Add(E_ss_t[i] >= 0)
    solver.Add(E_ss_t[-1] == final_SoC * EV_testing.E_max_capacity)
    solver.Minimize( solver.Sum( [P_ess_in_t[i] * market_prices[i]  for i in range(max_number_of_intervals)] ) ) # - P_ess_out_t[i] * prices_data['prices'][i]

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())
    else:
        print('The problem does not have an optimal solution.')
    
    P_in_t_array = np.zeros((max_number_of_intervals))
    # P_out_t_array = np.zeros((max_number_of_intervals))
    E_ss_t_array = np.zeros((max_number_of_intervals))
    for i in range(max_number_of_intervals):
        P_in_t_array[i] = P_ess_in_t[i].solution_value()
        # P_out_t_array[i] = P_ess_out_t[i].max_number_of_intervalssolution_value()
        E_ss_t_array[i] = E_ss_t[i].solution_value()
    
    plt.figure(figsize=(16,9))
    plt.title (' Smart charging: low cost policy', fontdict={'fontsize':14})
    plt.ylabel(' - kW - ', fontsize=14)
    time = np.arange(max_number_of_intervals)
    timeslots = pd.date_range("00:00", periods = max_number_of_intervals, freq="15min").strftime('%H:%M:%S')
    plt.plot(time, P_in_t_array, label = ' P_ess_in_t ' )
    plt.plot(time, E_ss_t_array, label = ' E_ss_t ' )
    # plt.plot(time, -P_out_t_array, label = ' P_ess_out_t ' )
    plt.legend(loc=2, prop={'size': 14})
    plt.xticks(time, timeslots, rotation='vertical', fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis = 'y')
    plt.show()

    cost_of_charging = np.sum( P_in_t_array * market_prices[0:max_number_of_intervals] ) / 1000 / 4
    duration = find_duration_of_charging_in_minutes(P_in_t_array, time_resolution)

    return P_in_t_array, cost_of_charging, duration

def run_opt_2nd(EV_testing, market_prices, max_number_of_intervals:int= 20, final_SoC:float = 1.0):
    """
    2nd: Minimize the time needed for charging ( Cost is indiferrent ) 
    + desired final SoC is an additional input (default is 100%) - > car charges with maximum power.  

    """
    solver = pywraplp.Solver.CreateSolver('GLOP')

    E_ss_t = [solver.NumVar(0.0, solver.infinity(), 'E_ess_'+ str(i) ) for i in range(max_number_of_intervals)]
    P_ess_in_t = [solver.NumVar(0.0, solver.infinity(), 'P_ess_in_'+ str(i) ) for i in range(max_number_of_intervals)]

    for i in range(max_number_of_intervals):
        solver.Add( P_ess_in_t[i] <= EV_testing.P_max ) # + P_ess_out_t[i]
        if i == max_number_of_intervals-1:
            solver.Add( P_ess_in_t[i] == 0 )
        if i != 0:
            solver.Add(solver.Sum([power_to_energy_conversion_ratio * P_ess_in_t[j] * EV_testing.hetta_in for j in range(i)])  + EV_testing.E_ss_0 == E_ss_t[i] ) # - solver.Sum([P_ess_out_t[j] * EV_testing.hetta_out for j in range(i)])
        else:
            solver.Add(E_ss_t[i] == EV_testing.E_ss_0)
        solver.Add(E_ss_t[i] <= EV_testing.E_max_capacity)
        solver.Add(E_ss_t[i] >= 0)
    solver.Add(E_ss_t[-1] == final_SoC * EV_testing.E_max_capacity)

    auxiliary_array = range(max_number_of_intervals, 0, -1)
    solver.Maximize( solver.Sum( [P_ess_in_t[i] * auxiliary_array[i]  for i in range(max_number_of_intervals)] ) ) # - P_ess_out_t[i] * prices_data['prices'][i]

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())
    else:
        print('The problem does not have an optimal solution.')

    P_in_t_array = np.zeros((max_number_of_intervals))
    # P_out_t_array = np.zeros((max_number_of_intervals))
    E_ss_t_array = np.zeros((max_number_of_intervals))
    for i in range(max_number_of_intervals):
        P_in_t_array[i] = P_ess_in_t[i].solution_value()
        # P_out_t_array[i] = P_ess_out_t[i].max_number_of_intervalssolution_value()
        E_ss_t_array[i] = E_ss_t[i].solution_value()

    plt.figure(figsize=(16,9))
    plt.title (' Smart charging: minimum time policy', fontdict={'fontsize':14})
    plt.ylabel(' - kW - ', fontsize=14)
    time = np.arange(max_number_of_intervals)
    timeslots = pd.date_range("00:00", periods = max_number_of_intervals, freq="15min").strftime('%H:%M:%S')
    plt.plot(time, P_in_t_array, label = ' P_ess_in_t ' )
    plt.plot(time, E_ss_t_array, label = ' E_ss_t ' )
    # plt.plot(time, -P_out_t_array, label = ' P_ess_out_t ' )
    plt.legend(loc=2, prop={'size': 14})
    plt.xticks(time, timeslots, rotation='vertical', fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis = 'y')
    plt.show()

    cost_of_charging = np.sum( P_in_t_array * market_prices[0:max_number_of_intervals] ) / 1000 / 4
    # to find last element of P_in_t_array that is not zero.
    duration = find_duration_of_charging_in_minutes(P_in_t_array, time_resolution)
    
    return P_in_t_array, cost_of_charging, duration

def run_opt_3rd(EV_testing, market_prices, max_number_of_intervals:int= 20, final_SoC:float = 1.0):
    """
    3rd: cost & time multiobjective optimization. 
    + desired final SoC is an additional input (default is 100%)
    Practically, it is cost-optimal with a minimum amount of power in.

    """
    solver = pywraplp.Solver.CreateSolver('GLOP')

    E_ss_t = [solver.NumVar(0.0, solver.infinity(), 'E_ess_'+ str(i) ) for i in range(max_number_of_intervals)]
    P_ess_in_t = [solver.NumVar(0.0, solver.infinity(), 'P_ess_in_'+ str(i) ) for i in range(max_number_of_intervals)]
    # P_ess_out_t = [solver.NumVar(0.0, solver.infinity(), 'P_ess_out_'+ str(i) ) for i in range(max_number_of_intervals)]

    print('Number of variables =', solver.NumVariables())

    for i in range(max_number_of_intervals):
        solver.Add(P_ess_in_t[i] <= EV_testing.P_max ) # + P_ess_out_t[i]
        # solver.Add(P_ess_in_t[i] >= minimum_charge_rate * EV_testing.P_max )
        if i != 0:
            solver.Add(solver.Sum([power_to_energy_conversion_ratio * P_ess_in_t[j] * EV_testing.hetta_in for j in range(i)])  + EV_testing.E_ss_0 == E_ss_t[i] ) # - solver.Sum([P_ess_out_t[j] * EV_testing.hetta_out for j in range(i)])
        else:
            solver.Add(E_ss_t[i] == EV_testing.E_ss_0)
        solver.Add(E_ss_t[i] <= EV_testing.E_max_capacity)
        solver.Add(E_ss_t[i] >= 0)
    solver.Add(E_ss_t[-1] == final_SoC * EV_testing.E_max_capacity)
    # Creatiing auxiliary array for pareto optimization.
    offset = min(market_prices)
    step = max(market_prices) / max_number_of_intervals
    num = max_number_of_intervals
    auxiliary_array = np.arange(0,num) * step + offset

    # solver.Maximize( solver.Sum( [P_ess_in_t[i] * auxiliary_array[i]  for i in range(max_number_of_intervals)] ) )

    solver.Minimize( solver.Sum( [P_ess_in_t[i] * (market_prices[i] + auxiliary_array[i])  for i in range(max_number_of_intervals)] ) ) # - P_ess_out_t[i] * prices_data['prices'][i]

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())
    else:
        print('The problem does not have an optimal solution.')
    
    P_in_t_array = np.zeros((max_number_of_intervals))
    # P_out_t_array = np.zeros((max_number_of_intervals))
    E_ss_t_array = np.zeros((max_number_of_intervals))
    for i in range(max_number_of_intervals):
        P_in_t_array[i] = P_ess_in_t[i].solution_value()
        # P_out_t_array[i] = P_ess_out_t[i].max_number_of_intervalssolution_value()
        E_ss_t_array[i] = E_ss_t[i].solution_value()
    
    plt.figure(figsize=(16,9))
    plt.title (' Smart charging: multi-objective policy', fontdict={'fontsize':14})
    plt.ylabel(' - kW - ', fontsize=14)
    time = np.arange(max_number_of_intervals)
    timeslots = pd.date_range("00:00", periods = max_number_of_intervals, freq="15min").strftime('%H:%M:%S')
    plt.plot(time, P_in_t_array, label = ' P_ess_in_t ' )
    plt.plot(time, E_ss_t_array, label = ' E_ss_t ' )
    # plt.plot(time, -P_out_t_array, label = ' P_ess_out_t ' )
    plt.legend(loc=2, prop={'size': 14})
    plt.xticks(time, timeslots, rotation='vertical', fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis = 'y')
    plt.show()

    cost_of_charging = np.sum( P_in_t_array * market_prices[0:max_number_of_intervals] ) / 1000 / 4
    duration = find_duration_of_charging_in_minutes(P_in_t_array, time_resolution)

    return P_in_t_array, cost_of_charging, duration


class EV_model:
    def __init__(self, E_max, c_r, E_0, h_in = 1, h_out = 1):
        self.E_max_capacity = E_max
        self.c_rate = c_r
        self.P_max = self.c_rate * self.E_max_capacity
        self.E_ss_0 = E_0
        self.hetta_in = h_in 
        self.hetta_out = h_out


