import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import cvxpy as cp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from ortools.linear_solver import pywraplp
print('hello world!!')



url = 'https://raw.githubusercontent.com/GeorgiosSkaltsis/load_dataset/main/merged.csv'
df1 = pd.read_csv(url)
Customers_data = []
Customers_data = {}
number_of_assets = 64
dimension_of_flexibility = 4  # Assuming that we are interested in a DR with duration of 1 hour.
forecasted_flexibility = np.zeros((dimension_of_flexibility, number_of_assets))
# import ipdb; ipdb.set_trace()
for i in range(number_of_assets):
  # import ipdb; ipdb.set_trace()
  Customers_data[i] = pd.concat([df1[i * 24 * 92:(i+1) * 24 * 92]],  ignore_index=True)
  # Customers_data[i] = pd.concat([df1[i * 3:(i+1) * 3]],  ignore_index=True)
  # print(Customers_data[i])
  nmp = Customers_data[i].to_numpy()

  forecasted_flexibility[:,i] = nmp[0:dimension_of_flexibility,1] / 1000 # assuming that data are given in Watts

####################      REQUEST OF FLEXIBILITYSet-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process


flexibility_requested = 12 # This is assumed to be 5 kW

####################    FORMULATION OF THE OPTIMIZATION SCHEME

flexibility_requested_array = flexibility_requested * np.ones(dimension_of_flexibility)
print('Shape of flexibility_requested_array is  ', flexibility_requested_array.shape)

solution = np.zeros(number_of_assets)
# iteration = 0

# Create the mip solver with the SCIP backend.
solver = pywraplp.Solver.CreateSolver('SCIP') # GUROBI_MIP or 'SCIP' or 'CPLEX_MIP'

# x[i, j] is an array of 0-1 variables, which will be 1
# if worker i is assigned to task j.
x = {}
# import ipdb; ipdb.set_trace()
for i in range(number_of_assets):
    x[ i ] = solver.IntVar(0, 1, '')

# Each worker is assigned to at most 1 task.
# sum of forcasted flexibility is higher than flexibility requested
for j in range(dimension_of_flexibility):
    solver.Add( solver.Sum([x[i] * forecasted_flexibility[j, i] for i in range( number_of_assets )]) >= flexibility_requested)
print('Number of constraints =', solver.NumConstraints())
# for j in range(dimension_of_flexibility):
solver.Minimize( solver.Sum( solver.Sum([x[i] * forecasted_flexibility[j, i] for i in range( number_of_assets )]) for j in range(dimension_of_flexibility) ) )


import ipdb; ipdb.set_trace()
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print('Solution:')
    print('Objective value =', solver.Objective().Value())
    # print('x =', x[i].solution_value())
else:
    print('The problem does not have an optimal solution.')

    print('\nAdvanced usage:')
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())
    print('Problem solved in %d branch-and-bound nodes' % solver.nodes())


# print('Total number of assets employed for the job is : ' , sum(b.value))
# print('This is the value of the aggregated flex, so far: ' , forecasted_flexibility.dot(b.value))
plt.figure(3)
plt.title ('Flexibility requested and employed ')
plt.xlabel('Time - quarters of the hour')
plt.ylabel(' - kW - ')
aggregated_flexibility = np.zeros((dimension_of_flexibility))
timeslots = ['10:00','10:15','10:30','10:45']
time = np.arange(dimension_of_flexibility)
for i in range(number_of_assets):
    if x[i].solution_value():
        aggregated_flexibility += forecasted_flexibility[:,i]
        plt.plot(timeslots, forecasted_flexibility[:,i])
        plt.grid(True)
plt.plot(timeslots, flexibility_requested_array, label = 'Requested Flexibility' )
plt.plot(timeslots, aggregated_flexibility, label = 'Aggregated Flexibility' )
plt.legend()
plt.show()

