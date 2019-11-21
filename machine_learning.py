from sklearn import preprocessing
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn import neighbors
from sklearn.svm import SVR
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn import svm
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
import pandas as pd


def machine_learning(test_dataset):
    train_X =pd.read_csv('/Users/chengmingcui/Desktop/9321/dataset/X_training_data.csv')
    train_Y = pd.read_csv('/Users/chengmingcui/Desktop/9321/dataset/Y_training_data.csv')
    train_X = train_X.drop(['Unnamed: 0'], axis=1)
    train_Y = train_Y.drop(['Unnamed: 0'], axis=1)
    text_x_data = pd.DataFrame(test_dataset, columns = ['Distance', 'Bedroom2', 'Bathroom', 'Car', 'Landsize',
       'BuildingArea', 'YearBuilt', 'Lattitude', 'Longtitude', 'flag_suburb',
       'flag_street_Address', 'flag_type', 'flag_regionname'])
    min_max_scaler = preprocessing.MinMaxScaler()
    processed_x_train = min_max_scaler.fit_transform(train_X)
    processed_x_test = min_max_scaler.fit_transform(text_x_data)
    
    model =  RandomForestRegressor(n_estimators=100, max_features='sqrt')
    model.fit(processed_x_train, train_Y)
    final = model.predict(processed_x_test) 
#     identifier = []
#     w = -1
#     for i in final:
#         w +=1
#         identifier.append(w)
    pd_final = pd.DataFrame(final)
    pd_final.rename(columns = {pd_final.columns[0] : 'Price'} , inplace = True)
    final_csv = test_dataset.join(pd_final)
#     final_csv['Identifier'] = identifier
#     final_csv = final_csv.set_index(['Identifier'])
    final_csv.to_csv('final_predict.csv')
    
    return 
    

