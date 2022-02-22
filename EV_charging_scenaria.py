import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import cvxpy as cp
from EV_model_n_optimization import run_opt_1st, run_opt_2nd, run_opt_3rd
from EV_model_n_optimization import EV_model
from __init__ import power_to_energy_conversion_ratio, time_resolution
# from ortools.constraint_solver import routing_enums_pb2
# from ortools.constraint_solver import pywrapcp
# from ortools.linear_solver import pywraplp

# Configurable parameters and assumed prices
max_number_of_intervals = 16
final_SoC = 1
prices_data = pd.read_csv ('prices_example.csv')


plt.figure(figsize=(16,9))
plt.title (' Forecasted Prices ', fontdict={'fontsize':14})
# plt.xlabel('', fontsize=14)
plt.ylabel(' - euro / MWh - ', fontsize=14)
time_96 = np.arange(max_number_of_intervals)
timeslots_96 = pd.date_range("00:00", periods=max_number_of_intervals, freq=str(time_resolution)+"min").strftime('%H:%M:%S')

prices_array = prices_data['prices'].to_numpy()

plt.plot(time_96, prices_array[0:max_number_of_intervals] , label = ' Forecasted prices [euro / MWh] ' )
# plt.legend()
plt.legend(loc=2, prop={'size': 14})
plt.xticks(time_96, timeslots_96, rotation='vertical', fontsize=14)
plt.yticks(fontsize=14)
plt.ylim(ymin=0)
plt.grid(axis = 'y')
# plt.grid(True)
plt.show()


## Defining EVs' electric characteristics 

E_max_capacity =  15 # [kWh]. 
c_rate = 0.6 # that is P_max for charging or discharging is 30% of Emax_capacity
P_max = c_rate * E_max_capacity
SoC_0 = 0.3 # Initial state of charge is 20%
E_ss_0 = SoC_0 * E_max_capacity
hetta_in = 0.8
hetta_out = 0.8

EV_testing_car = EV_model(E_max_capacity, c_rate, E_ss_0, hetta_in, hetta_in) 


# The car-driver arrices in the smart charger with aforementioned initial values.
# The smart-charger will offer him 3-4 different charging-products with different values, based on different optimization strategies.
# import ipdb; ipdb.set_trace()
# 1st: cost-optimal (time is indifferent) option. + desired final SoC is an additional input (default is 100%) + an upper limit for time constraint, e.g. maximum 5 hours.
[charging_strategy_1st_policy, cost_1st_policy, duration_1st] = run_opt_1st(EV_testing_car, prices_array, max_number_of_intervals, final_SoC ) 

# print('The optimal cost for the low cost strategy is equal to : ' , cost_1st_policy)
# # 2nd: time is the priority (that is, to charge fast as possible. Cost is indiferrent). + desired final SoC is an additional input (default is 100%) - > car charges with maximum power. 
[charging_strategy_2nd_policy, cost_2nd_policy, duration_2nd] = run_opt_2nd(EV_testing_car, prices_array, max_number_of_intervals , final_SoC) 

# # 3rd: cost & time multiobjective optimization. + desired final SoC is an additional input (default is 100%)
# Practically, it is cost-optimal with a minimum amount of power in.

[charging_strategy_3rd_policy, cost_3rd_policy, duration_3rd] = run_opt_3rd(EV_testing_car, prices_array, max_number_of_intervals , final_SoC ) 

# # 4th: cost & time multiobjective optimization. + desired final SoC is an additional input (default is 100%)
# [charging_strategy_3rd_policy, cost_3rd_policy] = run_opt_4th(EV_testing_car,) 

plt.figure(figsize=(16,9))
plt.title (' Smart charging: Comparison of three policies', fontdict={'fontsize':14})
plt.ylabel(' - kW - ', fontsize=14)
time = np.arange(max_number_of_intervals)
timeslots = pd.date_range("00:00", periods = max_number_of_intervals, freq="15min").strftime('%H:%M:%S')
plt.plot(time, charging_strategy_1st_policy, label = ' P_charging_1st: cost-optimal ' + str(final_SoC * 100) + ' % charging, with cost =  ' + str("{:.2f}".format(cost_1st_policy)) + ' euros and duration: ' + str(duration_1st) + 'minutes' )
plt.plot(time, charging_strategy_2nd_policy, label = ' P_charging_2nd: time-optimal '+ str(final_SoC * 100) +' % charging, with cost =  ' + str("{:.2f}".format(cost_2nd_policy)) + ' euros and duration: ' + str(duration_2nd) + 'minutes' )
plt.plot(time, charging_strategy_3rd_policy, label = ' P_charging_3rd: multi-objective '+ str(final_SoC * 100) +' % charging, with cost =  ' + str("{:.2f}".format(cost_3rd_policy)) + ' euros and duration: ' + str(duration_3rd) + 'minutes' )

# plt.plot(time, -P_out_t_array, label = ' P_ess_out_t ' )
plt.legend(loc=2, prop={'size': 14})
plt.xticks(time, timeslots, rotation='vertical', fontsize=14)
plt.yticks(fontsize=14)
plt.grid(axis = 'y')
plt.ylim(ymax = P_max + 2)
plt.show()