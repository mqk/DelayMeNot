import pandas as pd

def read_carrier_dict():
    df = pd.read_table('data/carriers.txt',header=None,names=['Code','Name'])
    code_to_name = dict(zip(df['Code'],df['Name']))
    name_to_code = dict(zip(df['Name'],df['Code']))

    return code_to_name, name_to_code

def read_airport_dict():
    df = pd.read_table('data/airports.txt',header=None,names=['Code','Name'])
    code_to_name = dict(zip(df['Code'],df['Name']))
    name_to_code = dict(zip(df['Name'],df['Code']))

    return code_to_name, name_to_code
