import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import json

from __init__ import number_of_prosumers
from utilities import create_random_flexibility_dataFrame, create_json_flexibility_event
from database.endpoints import get_users, get_user, delete_event, post_flexibility, get_event, get_events_by_type

print( 'Here we make a function that creates realistic flexibility events - data per asset.' )

# Define date of interest.
date = dt.datetime.now() # pytz.utc
start_date = dt.datetime(date.year, date.month, date.day) - dt.timedelta(hours=24)
end_date = start_date + dt.timedelta(days=1)

print( 'number_of_prosumers is :' , number_of_prosumers )# json.load(file object)
flexibility_event = open('Updated_Asset_Flexibility_Example.json')
data = json.load(flexibility_event)

path='C:\\Users\\gskaltsis\\Desktop\\coding\\parity_tests_v2\\files\\consumption_and_flexibility_examples\\'


# Creating csv files containing the necessary information
# for i in range(number_of_prosumers):
#     P_cons_n_flex = create_random_flexibility_dataFrame(start_date)
#     P_cons_n_flex.to_csv(path + 'consumption_and_flexibility_example_'+str(i)+'.csv')

# Save information in json-format aggreed with hypertech.
# for i in range(number_of_prosumers):
#     P_loaded_cons_n_flex = pd.read_csv (path + 'consumption_and_flexibility_example_'+str(i)+'.csv') 
#     data_in_json = create_json_flexibility_event(P_loaded_cons_n_flex, end_date)
#     file_name = 'flex_data\\flex_event_data_'+str(i)+'.json' # 
#     # import ipdb; ipdb.set_trace()
#     with open(file_name, 'w') as fp:
#         json.dump(data_in_json, fp)

## To post flexibility events on the database. posting is easy, but it should be done in a way that events can be retrieved.

# users = get_users()
# for i in range(len(users['users'])):
#     print ( 'The id of user ', i ,' is : ' , users['users'][i]['user']['id'] )
# start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
# end_date = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
# for i in range(number_of_prosumers):
#     with open('flex_data\\flex_event_data_'+ str(i) + '.json', 'r') as f:
#         # read the data
#         data = f.read()
#         # then load it using json.loads()
#         final = json.loads(data)
#         post_flexibility( final )
# import ipdb; ipdb.set_trace()

# event_is = get_event( final['event']['id'] )
# events_are = get_events_by_type(start_date, end_date, type = 'FlexibilityForecastAsset')
# delete_event(identity = final['event']['id'])



testing_feid = pd.DataFrame({
                                'consumptionCapacity': [2500],
                                'generationCapacity':[3000],
                                'storageCapacity':[2000], 
                                'contractedPower': [21000], 
                                'market': 1,
                                'dr_type':0
                                }, 
                                index = ['vFEID120'])
#convert the dataframe to json
json_df = testing_feid.to_json()
import ipdb; ipdb.set_trace()
parsed_dict = json.loads(json_df)
parsed_df = pd.DataFrame(parsed_dict)


