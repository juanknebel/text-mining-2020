import pandas as pd 
import numpy as np
from tabulate import tabulate


data = pd.read_csv("dreams.csv",sep=';')

print(tabulate(data.head()))





