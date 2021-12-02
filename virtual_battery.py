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