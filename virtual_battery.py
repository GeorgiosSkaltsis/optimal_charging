import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import cvxpy as cp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from ortools.linear_solver import pywraplp
print('hello world!!')

load_data = pd.read_csv ('consumption_and_flexibility_example.csv')
prices_data = pd.read_csv ('prices_example.csv')


flex_up = load_data['flex_up'] - load_data['consumption'] 
flex_down = load_data['consumption'] - load_data['flexibility_down'] 


plt.figure(figsize=(16,9))
plt.title (' Flexibility monitoring', fontdict={'fontsize':14})
# plt.xlabel('', fontsize=14)
plt.ylabel(' - kW - ', fontsize=14)
time_96 = np.arange(96)
timeslots_96 = pd.date_range("00:00", "23:59", freq="15min").strftime('%H:%M:%S')
for i in range(len(time_96)):
    if (i / 8).is_integer() == False:
        timeslots_96.values[i] = ''

consumption_96 = load_data['consumption'].to_numpy()
flexibility_down_96 = load_data['flexibility_down'].to_numpy()
flexibility_up_96 = load_data['flex_up'].to_numpy()

plt.plot(time_96, consumption_96, label = ' Forecasted consumption ' )
plt.plot(time_96, flexibility_down_96, label = ' Forecasted flexibility downwards ' )
plt.plot(time_96,flexibility_up_96, label = ' Forecasted flexibility upwards ' )
# plt.legend()
plt.legend(loc=2, prop={'size': 14})
plt.xticks(time_96, timeslots_96, rotation='vertical', fontsize=14)
plt.yticks(fontsize=14)
plt.ylim(ymin=0)
plt.grid(axis = 'y')
# plt.grid(True)
plt.show()


plt.figure(figsize=(16,9))
plt.title (' Flexibility monitoring', fontdict={'fontsize':14})
# plt.xlabel('', fontsize=14)
plt.ylabel(' - euro / MWh - ', fontsize=14)
time_96 = np.arange(96)
timeslots_96 = pd.date_range("00:00", "23:59", freq="15min").strftime('%H:%M:%S')
for i in range(len(time_96)):
    if (i / 8).is_integer() == False:
        timeslots_96.values[i] = ''

prices_array = prices_data['prices'].to_numpy()

plt.plot(time_96, prices_array , label = ' Forecasted prices [euro / MWh] ' )
# plt.legend()
plt.legend(loc=2, prop={'size': 14})
plt.xticks(time_96, timeslots_96, rotation='vertical', fontsize=14)
plt.yticks(fontsize=14)
plt.ylim(ymin=0)
plt.grid(axis = 'y')
# plt.grid(True)
plt.show()

P_max = np.maximum(flex_up.max(), flex_down.max())
E_max_capacity = P_max * 15 # [kWh]. That is, the maximum storage capacity is that if empty it can keep charging with P_max for an hour untill fully charged.
E_ss_0 = 0.5 * E_max_capacity
hetta_in = 0.8
hetta_out = 0.8

solver = pywraplp.Solver.CreateSolver('GLOP')

E_ss_t = [solver.NumVar(0.0, solver.infinity(), 'E_ess_'+ str(i) ) for i in range(len(flex_down))]
P_ess_in_t = [solver.NumVar(0.0, solver.infinity(), 'P_ess_in_'+ str(i) ) for i in range(len(flex_down))]
P_ess_out_t = [solver.NumVar(0.0, solver.infinity(), 'P_ess_out_'+ str(i) ) for i in range(len(flex_down))]

print('Number of variables =', solver.NumVariables())


#  solver.Sum( solver.Sum([x[i] * forecasted_flexibility[j, i] for i in range( number_of_assets )]) for j in range(dimension_of_flexibility) )
# solver.Sum([x[i] * forecasted_flexibility[j, i] for i in range( number_of_assets )]) >= flexibility_requested
# constraints = []


for i in range(len(flex_down)):
    solver.Add(P_ess_in_t[i] + P_ess_out_t[i] <=P_max)
    if i != 0:
        solver.Add(solver.Sum([P_ess_in_t[j] * hetta_in for j in range(i)]) - solver.Sum([P_ess_out_t[j] * hetta_out for j in range(i)]) + E_ss_0 == E_ss_t[i] )
    else:
        solver.Add(E_ss_t[i] == E_ss_0)
    solver.Add(E_ss_t[i] <= E_max_capacity)
    solver.Add(E_ss_t[i] >= 0)
solver.Add(E_ss_t[-1] == E_ss_0)
solver.Minimize( solver.Sum( [P_ess_in_t[i] * prices_data['prices'][i] - P_ess_out_t[i] * prices_data['prices'][i] for i in range(len(flex_down))] ) )

status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print('Solution:')
    print('Objective value =', solver.Objective().Value())
else:
    print('The problem does not have an optimal solution.')

print('\nAdvanced usage:')
print('Problem solved in %f milliseconds' % solver.wall_time())
print('Problem solved in %d iterations' % solver.iterations())
# print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
    


plt.figure(figsize=(16,9))
plt.title (' Flexibility monitoring', fontdict={'fontsize':14})
# plt.xlabel('', fontsize=14)
plt.ylabel(' - kW - ', fontsize=14)
time_96 = np.arange(96)
timeslots_96 = pd.date_range("00:00", "23:59", freq="15min").strftime('%H:%M:%S')
P_in_t_array = np.zeros((len(flex_down)))
P_out_t_array = np.zeros((len(flex_down)))
E_ss_t_array = np.zeros((len(flex_down)))
for i in range(len(time_96)):
    P_in_t_array[i] = P_ess_in_t[i].solution_value()
    P_out_t_array[i] = P_ess_out_t[i].solution_value()
    E_ss_t_array[i] = E_ss_t[i].solution_value()
    if (i / 8).is_integer() == False:
        timeslots_96.values[i] = ''
# .solution_value()
plt.plot(time_96, P_in_t_array, label = ' P_ess_in_t ' )
plt.plot(time_96, -P_out_t_array, label = ' P_ess_out_t ' )


# plt.legend()
plt.legend(loc=2, prop={'size': 14})
plt.xticks(time_96, timeslots_96, rotation='vertical', fontsize=14)
plt.yticks(fontsize=14)
# plt.ylim(ymin=0)
plt.grid(axis = 'y')
# plt.grid(True)
plt.show()


plt.figure(figsize=(16,9))
plt.title (' Flexibility monitoring', fontdict={'fontsize':14})
# plt.xlabel('', fontsize=14)
plt.ylabel(' - kW - ', fontsize=14)
time_96 = np.arange(96)
timeslots_96 = pd.date_range("00:00", "23:59", freq="15min").strftime('%H:%M:%S')
for i in range(len(time_96)):
    if (i / 8).is_integer() == False:
        timeslots_96.values[i] = ''

consumption_96 = load_data['consumption'].to_numpy()
flexibility_down_96 = load_data['flexibility_down'].to_numpy()
flexibility_up_96 = load_data['flex_up'].to_numpy()

plt.plot(time_96, consumption_96, label = ' Forecasted consumption ' )
plt.plot(time_96, flexibility_down_96, label = ' Forecasted flexibility downwards ' )
plt.plot(time_96,flexibility_up_96, label = ' Forecasted flexibility upwards ' )
plt.plot(time_96,consumption_96 + P_in_t_array - P_out_t_array, label = ' Desired setpoint ' )

# plt.legend()
plt.legend(loc=2, prop={'size': 14})
plt.xticks(time_96, timeslots_96, rotation='vertical', fontsize=14)
plt.yticks(fontsize=14)
plt.ylim(ymin=0)
plt.grid(axis = 'y')
# plt.grid(True)
plt.show()


plt.figure(figsize=(16,9))
plt.title (' Flexibility monitoring', fontdict={'fontsize':14})
# plt.xlabel('', fontsize=14)
plt.ylabel(' - kW - ', fontsize=14)
time_96 = np.arange(96)
timeslots_96 = pd.date_range("00:00", "23:59", freq="15min").strftime('%H:%M:%S')
for i in range(len(time_96)):
    if (i / 8).is_integer() == False:
        timeslots_96.values[i] = ''

consumption_96 = load_data['consumption'].to_numpy()
flexibility_down_96 = load_data['flexibility_down'].to_numpy()
flexibility_up_96 = load_data['flex_up'].to_numpy()

desired_setpoint = consumption_96 + P_in_t_array - P_out_t_array
prices_array = prices_data['prices'].to_numpy()
plt.plot(time_96, consumption_96, label = ' Forecasted consumption ' )
# plt.plot(time_96, flexibility_down_96, label = ' Forecasted flexibility downwards ' )
# plt.plot(time_96,flexibility_up_96, label = ' Forecasted flexibility upwards ' )
plt.plot(time_96, desired_setpoint, label = ' Desired setpoint ' )
plt.plot(time_96, prices_array / 10 , label = ' Forecasted prices ' )
# plt.legend()
plt.legend(loc=2, prop={'size': 14})
plt.xticks(time_96, timeslots_96, rotation='vertical', fontsize=14)
plt.yticks(fontsize=14)
plt.ylim(ymin=0)
plt.grid(axis = 'y')
# plt.grid(True)
plt.show()

# import ipdb; ipdb.set_trace()

baseline_cost = sum(consumption_96 * prices_array) / 1000 / 4
optimised_setpoint_cost = sum(desired_setpoint * prices_array) / 1000 / 4