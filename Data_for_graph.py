import pandas as pd
import matplotlib.pyplot as plt

def graph1 (year):
   df = pd.read_csv("melb.csv")
   df1 = df.loc[:, ["Price", "YearBuilt"]]
   df1 = df1.query("YearBuilt >= @year-5 and YearBuilt <= @year+5")
   df1 = df1.groupby(["YearBuilt"]).mean()
   df1.plot.bar()
   plt.show()
   return df1

def graph2(suburb, year):
    df = pd.read_csv("melb.csv")
    df1 = df.query("Suburb == @suburb")
    df1 = df1.loc[:, ["Price", "YearBuilt"]]
    df1 = df1.query("YearBuilt >= @year-5 and YearBuilt <= @year+5")
    df1 = df1.groupby("YearBuilt").mean()
    df1.plot.bar()
    plt.show()
    return df1

def graph3(distance):
    melb = pd.read_csv('melb.csv')
    cols_to_drop = ['Unnamed: 0']
    melb = melb.drop(cols_to_drop, axis=1)
    new_df= pd.DataFrame()
    new_df['Suburb']  =melb['Suburb']
    new_df['Distance'] = melb['Distance']
    new_df['Price'] = melb['Price']

    second_df = new_df.query('Distance >= @distance')
    columns = ['Suburb' , 'Price']
    third_df = second_df[columns]
    third_df = third_df.groupby(['Suburb']).mean()
    forth_df = third_df.sort_values(by = 'Price' , ascending = True)
    final_df = forth_df[:5]
    final_df.plot.bar()
    plt.show()
    return final_df

# if __name__ == "__main__":
#     graph3(5.0)
#     graph1(1999)
#     graph2("Richmond",1999)

