import numpy as np
import pandas as pd
from string import digits
from sklearn.feature_selection import SelectKBest
from scipy.stats import pearsonr
from matplotlib import pyplot as plt



ds = pd.read_csv('melb_data.csv')
cols_to_drop = ['Method','SellerG','Date','CouncilArea','Lattitude','Longtitude','Propertycount','Rooms','Postcode']
df = ds.drop(cols_to_drop, axis=1)
data = df.dropna()
data = data.reset_index(drop = True)

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
# print(ll)

data["flag_suburb"] = ll
# data
address = data["Address"].tolist()
final_address = []
# for i in address:
#     remove_digits = str.maketrans("","",digits)
#     res = i.translate(remove_digits).strip()
#     final_address.append(res)
for i in address:
    for j in range(len(i)):
        if i[j] == " ":
            res = i[j:].strip()
            final_address.append(res)
            break
# print(final_address)
data['street_Address'] = final_address
address_list = data['street_Address'].value_counts().index.tolist()
address_dict = {}
count = 0
for i in address_list:
    address_dict[i] = count
    count+=1

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

## data_final is the final dataset after data processing 
## flag_suburb means the suburb
## flag_street_Address means The name of the street where the house is located
## lag_type means the type of the house( house , unit, apartment)
## flag_regionname means the region of the house ( north, west, south, east)

data_final = data.drop(drop_col_second, axis=1)

## analyse data
data_final.corr()

##drop the data whicht correlation rate is lower than 0.2
drop_col_third = ['Distance' , 'flag_suburb' , 'flag_street_Address']
data_final_after = data_final.drop(drop_col_third, axis=1)
data_final_after





