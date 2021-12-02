import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import cvxpy as cp


def round_arround(value, threshold):
    if value > threshold:
        value  = 1
    else:
        value = 0
    return value

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


####################      REQUEST OF FLEXIBILITYSet-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process


flexibility_requested = 5 # This is assumed to be 5 kW

####################    FORMULATION OF THE OPTIMIZATION SCHEME

feasible_solution_not_found = True

flexibility_requested_array = flexibility_requested * np.ones(dimension_of_flexibility)
print('Shape of flexibility_requested_array is  ', flexibility_requested_array.shape)
assets_employed = 0
solution = np.zeros(number_of_assets)
iteration = 0
while feasible_solution_not_found:
    b_continuous = cp.Variable(number_of_assets)
    constr = []
    for i in range(dimension_of_flexibility):
        constr += [cp.sum(cp.multiply(forecasted_flexibility[i, :], b_continuous)) >= flexibility_requested - forecasted_flexibility[i,:].dot(solution) ]
    constr += [b_continuous >= 0,
                b_continuous <= 1]

    for i in range(number_of_assets):
        if solution[i] == 1:
            constr += [ b_continuous[i] == 0 ]
    prob = cp.Problem(cp.Minimize(cp.sum(forecasted_flexibility @ b_continuous)), constr)
    # import ipdb
    # ipdb.set_trace()
    prob.solve( verbose=True) #@ solver='GLPK_MI',
    # It should hold that forecasted_flexibility.dot(solution) + forecasted_flexibility.dot(b_continuous.value) should be very close to the requested.
    additional_assets = np.round(b_continuous.value)
    number_of_additional_assets = int(sum(additional_assets))
    
    assets_employed = int(sum(solution))

    print('This is the proposed solution feasibility status: ' , forecasted_flexibility.dot(solution) + forecasted_flexibility.dot(additional_assets) >= flexibility_requested_array)
    print('This is the value of the aggregated flex, so far: ' , forecasted_flexibility.dot(solution) + forecasted_flexibility.dot(additional_assets))
    if number_of_additional_assets == 0:
        min_of_max_s = 10000 # just a random very high value
        for i in range(number_of_assets):
            if solution[i] != 1 and np.amax(forecasted_flexibility[:,i]) < min_of_max_s:
                min_position = i
                min_of_max_s = np.amax(forecasted_flexibility[:,i])
        # import ipdb
        # ipdb.set_trace()
        additional_assets[min_position] = 1
        number_of_additional_assets = int(sum(additional_assets))
    if (forecasted_flexibility.dot(solution) + forecasted_flexibility.dot(additional_assets) >= flexibility_requested_array).all():
        
        feasible_solution_not_found = False
        final_constr = []
        b_binary = cp.Variable(number_of_additional_assets, integer=True)
        final_forecasted_flexibility = np.zeros((dimension_of_flexibility, number_of_additional_assets))
        counter = 0
        # import ipdb
        # ipdb.set_trace()
        for i in range(number_of_assets):
            if additional_assets[i] == 1:
                final_forecasted_flexibility[:, counter] = forecasted_flexibility[:, i]
                counter += 1
        # It should hold that: forecasted_flexibility.dot(solution) == final_forecasted_flexibility.dot(np.ones(assets_employed))
        for i in range(dimension_of_flexibility):
            final_constr += [cp.sum(cp.multiply(final_forecasted_flexibility[i, :], b_binary ))  + forecasted_flexibility[i,:].dot(solution) >= flexibility_requested]
        final_constr += [b_binary >= 0,
                    b_binary <= 1]
        
        prob = cp.Problem(cp.Minimize(cp.sum(final_forecasted_flexibility @ b_binary)), final_constr)
        prob.solve(solver='GLPK_MI', verbose=True)
        plt.figure(1)
        plt.title ('Flexibility requested and employed ')
        plt.xlabel('Time - quarters of the hour')
        plt.ylabel(' - kW - ')
        aggregated_flexibility = np.zeros((dimension_of_flexibility))
        timeslots = ['10:00','10:15','10:30','10:45']
        time = np.arange(dimension_of_flexibility)
        for i in range(number_of_additional_assets):
            if b_binary.value[i]:
                aggregated_flexibility += final_forecasted_flexibility[:,i]
                plt.plot(timeslots, final_forecasted_flexibility[:,i])
                plt.grid(True)
        for i in range(number_of_assets):
            if solution[i] == 1:
                aggregated_flexibility += forecasted_flexibility[:,i]
                plt.plot(timeslots, forecasted_flexibility[:,i])
                plt.grid(True)
        plt.plot(timeslots, flexibility_requested_array, label = 'Requested Flexibility' )
        plt.plot(timeslots, aggregated_flexibility, label = 'Aggregated Flexibility' )
        plt.legend()
        plt.show()
        counter = 0
        for i in range(number_of_assets):
            if additional_assets[i] == 1:
                if b_binary.value[counter] != 1:
                    additional_assets[i] = 0
                counter += 1
        # import ipdb
        # ipdb.set_trace()
        solution = additional_assets + solution
    else:
        solution = additional_assets + solution
    

    iteration += 1

# import ipdb; ipdb.set_trace()
############################### PRINTING AND HAVING FUN

print('Total number of assets employed for the job is : ' , sum(solution))

plt.figure(3)
plt.title ('Flexibility requested and employed ')
plt.xlabel('Time - quarters of the hour')
plt.ylabel(' - kW - ')
aggregated_flexibility = np.zeros((dimension_of_flexibility))
timeslots = ['10:00','10:15','10:30','10:45']
time = np.arange(dimension_of_flexibility)
for i in range(number_of_assets):
    if solution[i]:
        aggregated_flexibility += forecasted_flexibility[:,i]
        plt.plot(timeslots, forecasted_flexibility[:,i])
        plt.grid(True)
plt.plot(timeslots, flexibility_requested_array, label = 'Requested Flexibility' )
plt.plot(timeslots, aggregated_flexibility, label = 'Aggregated Flexibility' )
plt.legend()
print('This is the value of the aggregated flex, so far: ' , forecasted_flexibility.dot(solution))
plt.show()
