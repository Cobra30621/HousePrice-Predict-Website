import pandas as pd
import numpy as np
from sklearn.utils import shuffle


compare_data = pd.read_csv('compare/compare_index.csv')

compare_data = shuffle(compare_data)

compare_data_small = compare_data[0:300000]



compare_data_small.to_csv('compare/compare_index_small.csv',index=False)

# 400 : 100 = 130 : 309
