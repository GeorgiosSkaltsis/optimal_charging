import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import json
import uuid


def create_random_flexibility_dataFrame(start_date):
    consumption_96 = 2 +  np.random.poisson(lam=10.0, size=96)
    positive_deviation = 3 * np.random.rand(96)
    flexibility_up_96 = consumption_96 + positive_deviation
    flexibility_down_96 = consumption_96 - positive_deviation
    P_cons_n_flex = pd.DataFrame({'timestamp':pd.date_range(start_date,freq ='15min',periods=len(consumption_96)).strftime('%Y-%m-%dT%H:%M:%SZ'),\
                                    'consumption':consumption_96,'flex_up':flexibility_up_96,\
                                    'flexibility_down': flexibility_down_96 }) # , start='21/9/2020'
    # import ipdb; ipdb.set_trace()
    return P_cons_n_flex

def create_json_flexibility_event(P_cons_n_flex , end_date):
    flexibility_event = open('Updated_Asset_Flexibility_Example.json')
    # import ipdb; ipdb.set_trace()
    data_in_json = json.load(flexibility_event)
    # import ipdb; ipdb.set_trace()
    data_in_json['event']['id'] = str(uuid.uuid4())
    data_in_json['event']['type'] = "FlexibilityForecastAsset"
    data_in_json['event']['description'] = "A forecasted flexibility event - asset level"
    data_in_json['event']['dateTime'] =  P_cons_n_flex.timestamp[0]
    data_in_json['event']['sourceId'] = str(uuid.uuid4())
    data_in_json['event']['space'] =  ""

    data_in_json['event']['content'][0]['requestInfo']['uuid'] = data_in_json['event']['id']
    data_in_json['event']['content'][0]['requestInfo']['requestType'] = "explicit"
    data_in_json['event']['content'][0]['requestInfo']['requestScope'] = "assetLevel"
    data_in_json['event']['content'][0]['requestInfo']['assetUuid'] = data_in_json['event']['sourceId']
    data_in_json['event']['content'][0]['requestInfo']['startDate'] = P_cons_n_flex.timestamp[0]
    data_in_json['event']['content'][0]['requestInfo']['endDate'] = str(end_date)
    data_in_json['event']['content'][0]['requestInfo']['interval'] = "15 minutes"
    data_in_json['event']['content'][0]['requestInfo']['flexibilityEstimationMethod'] = "absoluteP"
    data_in_json['event']['content'][0]['requestInfo']['baselineEstimationMethod'] = "absoluteP"
    data_in_json['event']['content'][0]['requestInfo']['createdAt'] = P_cons_n_flex.timestamp[0]

    for i in range(len( data_in_json['event']['content'][0]['baselineForecasting'] )):
        data_in_json['event']['content'][0]['baselineForecasting'][i]['refDateTimeStart '] = P_cons_n_flex.timestamp[i]
        if i != len( data_in_json['event']['content'][0]['baselineForecasting'] ) - 1:
            data_in_json['event']['content'][0]['baselineForecasting'][i]['refDateTimeEnd'] = P_cons_n_flex.timestamp[i+1]
        else:
            data_in_json['event']['content'][0]['baselineForecasting'][i]['refDateTimeEnd'] = str(end_date)
        data_in_json['event']['content'][0]['baselineForecasting'][i]['mean'] = float(P_cons_n_flex['consumption'][i] * 1000 )# we need watt
        data_in_json['event']['content'][0]['baselineForecasting'][i]['unit'] = "W"
        data_in_json['event']['content'][0]['baselineForecasting'][i]['createdAt'] = P_cons_n_flex.timestamp[0]

        data_in_json['event']['content'][0]['flexibilityForecasting'][i]['refDateTimeStart '] = P_cons_n_flex.timestamp[i]
        if i != len( data_in_json['event']['content'][0]['flexibilityForecasting'] ) - 1:
            data_in_json['event']['content'][0]['flexibilityForecasting'][i]['refDateTimeEnd'] = P_cons_n_flex.timestamp[i+1]
        else:
            data_in_json['event']['content'][0]['flexibilityForecasting'][i]['refDateTimeEnd'] = str(end_date)
        data_in_json['event']['content'][0]['flexibilityForecasting'][i]['meanUp'] = float(P_cons_n_flex['flex_up'][i] * 1000) # we need watt
        data_in_json['event']['content'][0]['flexibilityForecasting'][i]['meanDown'] = float(P_cons_n_flex['flexibility_down'][i] * 1000 ) # we need watt
        data_in_json['event']['content'][0]['flexibilityForecasting'][i]['unit'] = "W"
        data_in_json['event']['content'][0]['flexibilityForecasting'][i]['createdAt'] = P_cons_n_flex.timestamp[0]

    # data_in_json = json.dumps(data_in_json, indent = 4)

    return data_in_json