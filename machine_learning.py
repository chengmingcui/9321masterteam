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



def machine_learning(input):
    train_X = pd.read_csv('X_training_data.csv')
    train_Y = pd.read_csv('Y_training_data.csv')
    train_X = train_X.drop(['Unnamed: 0'], axis=1)
    train_Y = train_Y.drop(['Unnamed: 0'], axis=1)

    # text_x_data = pd.DataFrame(input, columns=['Distance', 'Bedroom2', 'Bathroom', 'Car', 'Landsize',
    #                                                   'BuildingArea', 'YearBuilt', 'Lattitude', 'Longtitude',
    #                                                   'flag_suburb',
    #                                                   'flag_street_Address', 'flag_type', 'flag_regionname'])
    # columns = ['Distance', 'Bedroom2', 'Bathroom', 'Car', 'Landsize',
    #                                                              'BuildingArea', 'YearBuilt', 'Lattitude', 'Longtitude',
    #                                                              'flag_suburb',
    #                                                              'flag_street_Address', 'flag_type', 'flag_regionname']
    text_x_data= input.drop(['Identifier',"UserID"], axis=1)
    # print(text_x_data.to_string())

    min_max_scaler = preprocessing.MinMaxScaler()
    processed_x_train = min_max_scaler.fit_transform(train_X)
    processed_x_test = min_max_scaler.fit_transform(text_x_data)

    model = RandomForestRegressor(n_estimators=100, max_features='sqrt')
    model.fit(processed_x_train, train_Y)
    final = model.predict(processed_x_test)
    #     identifier = []
    #     w = -1
    #     for i in final:
    #         w +=1
    #         identifier.append(w)
    pd_final = pd.DataFrame(final)

    pd_final.rename(columns={pd_final.columns[0]: 'Price'}, inplace=True)
    print("***********input*********************")
    print(input.to_string())
    print("******************pd_final***********")
    print(pd_final.to_string())
    final_csv = input.join(pd_final)
    #final_csv.set_index(["Identifier"], inplace= True)
    #     final_csv['Identifier'] = identifier
    #     final_csv = final_csv.set_index(['Identifier'])
    #print(final_csv.to_string())

    return final_csv


def data_processing(input):
    region_to_flag = pd.read_csv('regionFlat.csv')
    street_to_flag = pd.read_csv('streetFlat.csv')
    suburb_to_flag = pd.read_csv('suburbFlat.csv')
    type_to_flag = pd.read_csv('typeFlat.csv')
    dict_region = region_to_flag.set_index('Region')['flat'].to_dict()
    dict_street = street_to_flag.set_index('strees')['flat'].to_dict()
    dict_suburb = suburb_to_flag.set_index('suburb')['flat'].to_dict()
    dict_type = type_to_flag.set_index('Type')['flat'].to_dict()

    flag_region = []
    flag_street = []
    flag_suburb = []
    flag_type = []
    for i in input['Suburb']:
        flag_suburb.append(dict_suburb[i])
    input['flag_suburd'] = flag_suburb

    for i in input['Street']:
        flag_street.append(dict_street[i])
    input['flag_street_Address'] = flag_street

    for i in input['Type']:
        flag_type.append(dict_type[i])
    input['flag_type'] = flag_type

    for i in input['Regionname']:
        flag_region.append(dict_region[i])
    input['flag_regionname'] = flag_region

    cols_to_drop = ['Suburb', 'Street', 'Type', 'Regionname']

    output = input.drop(cols_to_drop, axis=1)

    return output

if __name__ == "__main__":
    raw_data = {"Identifier":1,
                "UserID": 9,
                "Distance": 12,
                "Badroom2": 2,
                "Bathroom": 1,
                "Car": 1,
                "Landsize": 100,
                "BuildingArea": 90,
                "YearBuilt": 2008,
                "Lattitude": 130,
                "Longtitude": 130,
                "Suburb": "Gelnroy",
                "Street": "William St",
                "Type": "t",
                "Regionname": "Northern Metropolitan"
                }
    df1 = pd.DataFrame(
        columns=["Identifier", "UserID", "Distance", "Badroom2", "Bathroom", "Car", "Landsize", "BuildingArea",
                 "YearBuilt", "Lattitude",
                 "Longtitude", "Suburb", "Street", "Type", "Regionname"])


    # put the value into the dataset
    for key in raw_data:
        df1.loc[0, key] = raw_data[key]


    print(df1.to_string())
    df = pd.read_csv("user_houses.csv", usecols=["Identifier", "UserID", "Distance", "Badroom2", "Bathroom", "Car", "Landsize", "BuildingArea",
                 "YearBuilt", "Lattitude",
                 "Longtitude", "Suburb", "Street", "Type", "Regionname"])
    print(df.to_string())
    df =df.append(df1, ignore_index= True)
    print(df.to_string())
    # df1 =machine_learning(df)
    # print(df1.to_string())
    # print(df1.loc[1,"Price"])


