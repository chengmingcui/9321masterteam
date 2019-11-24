import numpy as np
import pandas as pd
from string import digits
from sklearn.feature_selection import SelectKBest
from scipy.stats import pearsonr
from matplotlib import pyplot as plt
from string import digits
from sklearn import svm
import os

os.getcwd()

ds = pd.read_csv('/Users/chengmingcui/Desktop/9321/melb_data.csv')
cols_to_drop = ['Method','SellerG','Date','CouncilArea','Propertycount','Rooms','Postcode']

df = ds.drop(cols_to_drop, axis=1)
data = df.dropna()
data = data.reset_index(drop = True)


## transform suburb to digit
suburb_list = data["Suburb"].value_counts().index.tolist()
data_dict_suburb = {}
flag = 0
for i in suburb_list:
    data_dict_suburb[i] = flag
    flag += 1
suburb = data["Suburb"].tolist()
ll = []
for i in suburb:
    ll.append(data_dict_suburb[i])

data["flag_suburb"] = ll
data.head()
address = data["Address"].tolist()
final_address = []
for i in address:
    for j in range(len(i)):
        if i[j] == " ":
            res = i[j:].strip()
            final_address.append(res)
            break
data['street_Address'] = final_address


address_list = data['street_Address'].value_counts().index.tolist()
address_dict = {}
count = 0
for i in address_list:
    address_dict[i] = count
    count+=1
    
##transform street to digit
street_address_list = data['street_Address'].tolist()
new_Address = []
for i in street_address_list:
    new_Address.append(address_dict[i])
data['flag_street_Address'] = new_Address

type_list = data['Type'].value_counts().index.tolist()
type_dict={}
count = 0
for i in type_list:
    type_dict[i] = count
    count+=1
flag_type= []
type_list_all = data['Type'].tolist()
for i in type_list_all:
    flag_type.append(type_dict[i])
data['flag_type'] = flag_type

## transform region to digit
Region = data['Regionname'].value_counts().index.tolist()
region_dict = {}
count = 0
for i in Region:
    region_dict[i] = count
    count += 1
region_list = data['Regionname'].tolist()
flag_regionname =[]
for i in region_list:
    flag_regionname.append(region_dict[i])
data['flag_regionname'] = flag_regionname


drop_col_second = ['Suburb','Address','Type','Regionname','street_Address']
data_final = data.drop(drop_col_second, axis=1)
## the final data
data_final



##the function remove the outlier from the data
def get_outliners(dataset, outliers_fraction=0.25):
    clf = svm.OneClassSVM(nu=0.95 * outliers_fraction + 0.05, kernel="rbf", gamma=0.1)
    clf.fit(dataset)
    result = clf.predict(dataset)
    return result
## the data after remove the outlier from the data
training_dataset = data_final[get_outliners(data_final, 0.15)==1]


## get the trainning data,testdata
input_cols =['Distance', 'Bedroom2', 'Bathroom', 'Car', 'Landsize',
       'BuildingArea', 'YearBuilt', 'Lattitude', 'Longtitude', 'flag_suburb',
       'flag_street_Address', 'flag_type','flag_regionname']
output_col = ['Price']
X = training_dataset[input_cols].astype(float)
Y = training_dataset[output_col].astype(float)
X= X.reset_index(drop = True)
Y = Y.reset_index(drop=True)
X[:3289].to_csv('X_training_data.csv')
X[3289:].to_csv('X_test_data.csv')
Y[:3289].to_csv('Y_training_data.csv')
Y[3289:].to_csv('Y_test_data.csv')
