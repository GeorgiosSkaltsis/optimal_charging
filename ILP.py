import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import cvxpy as cp


url = 'https://raw.githubusercontent.com/GeorgiosSkaltsis/load_dataset/main/merged.csv'
df1 = pd.read_csv(url)
Customers_data = []

Customers_data = {} # dataframe_collection = {} 
Data = {
  "average_consumption": [],
  "min_to_max": []
}
  # "variance":[]
# }

number_of_assets = 64
dimension_of_flexibility = 4  # Assuming that we are interested in a DR with duration of 1 hour.
forecasted_flexibility = np.zeros((dimension_of_flexibility, number_of_assets))

for i in range(number_of_assets):
  Customers_data[i] = pd.concat([df1[i * 24 * 92:(i+1) * 24 * 92]],  ignore_index=True)
  # Customers_data[i] = pd.concat([df1[i * 3:(i+1) * 3]],  ignore_index=True)
  # print(Customers_data[i])
  nmp = Customers_data[i].to_numpy()

  forecasted_flexibility[:,i] = nmp[0:dimension_of_flexibility,1] / 1000 # assuming that data are given in Watts

  Data["average_consumption"].append( Customers_data[i].mean(axis = 0).to_numpy() )
  Data["min_to_max"].append(np.max(nmp[:,1]) - np.min(nmp[:,1]) )
  # Data["variance"].append(Customers_data[i].var().to_numpy() )
# print(Customers_data[0])


####################      REQUEST OF FLEXIBILITY

flexibility_requested = 12 # This is assumed to be 5 kW

####################    FORMULATION OF THE OPTIMIZATION SCHEME
b = cp.Variable(number_of_assets, integer=True)
constr = []
flexibility_requested_array = flexibility_requested * np.ones(dimension_of_flexibility)
print('Shape of flexibility_requested_array is  ', flexibility_requested_array.shape)
for i in range(dimension_of_flexibility):
    constr += [cp.sum(cp.multiply(forecasted_flexibility[i, :], b)) >= flexibility_requested]
constr += [b >= 0,
            b <= 1]
prob = cp.Problem(cp.Minimize(cp.sum(forecasted_flexibility @ b)), constr)
# import ipdb
# ipdb.set_trace()
prob.solve(solver='GLPK_MI', verbose=True)

############################### PRINTING AND HAVING FUN

print('Total number of assets employed for the job is : ' , sum(b.value))
print('This is the value of the aggregated flex, so far: ' , forecasted_flexibility.dot(b.value))
plt.figure(3)
plt.title ('Flexibility requested and employed ')
plt.xlabel('Time - quarters of the hour')
plt.ylabel(' - kW - ')
aggregated_flexibility = np.zeros((dimension_of_flexibility))
timeslots = ['10:00','10:15','10:30','10:45']
time = np.arange(dimension_of_flexibility)
for i in range(number_of_assets):
    if b.value[i]:
        aggregated_flexibility += forecasted_flexibility[:,i]
        plt.plot(timeslots, forecasted_flexibility[:,i])
        plt.grid(True)
plt.plot(timeslots, flexibility_requested_array, label = 'Requested Flexibility' )
plt.plot(timeslots, aggregated_flexibility, label = 'Aggregated Flexibility' )
plt.legend()
plt.show()
