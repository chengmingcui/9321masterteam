def data_processing(input):
    region_to_flag = pd.read_csv('/Users/chengmingcui/Desktop/9321/String_to_Flat/regionFlat.csv')
    street_to_flag = pd.read_csv('/Users/chengmingcui/Desktop/9321/String_to_Flat/streetFlat.csv')
    suburb_to_flag = pd.read_csv('/Users/chengmingcui/Desktop/9321/String_to_Flat/suburbFlat.csv')
    type_to_flag = pd.read_csv('/Users/chengmingcui/Desktop/9321/String_to_Flat/typeFlat.csv')
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
    

    
    cols_to_drop = ['Suburb','Street','Type','Regionname']
    
    output =input.drop(cols_to_drop, axis=1)
    
    return output
    
