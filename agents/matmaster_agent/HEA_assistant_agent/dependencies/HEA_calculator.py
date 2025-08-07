import pandas as pd
import numpy as np
import os
import math
from featurebox.data.name_split import NameSplit
def HEA_calculate(input,binary_Hmix_data_path):
    VEC_dict = {'Li':1,'Be':2,'B':3,'C':4,'Mg':2,'Al':3,'Si':4,'Ti':4,'V':5,'Cr':6,'Mn':7,
                    'Fe':0,'Co':0,'Ni':0,'Cu':1,'Zn':2,'Ge':4,'Y':3,'Zr':4,'Nb':5,
                    'Mo':6,'Ru':0,'Rh':0,'Pd':0,'Ag':1,'Sn':4,'Ce':3.5,'Nd':3,'Hf':4,'Ta':5,'W':6,
                    'Re':7,'Ir':0,'Pt':0,'Au':1}
    radius_dict = {'Li':1.23,'Be':0.89,'B':0.82,'C':0.77,'Mg':1.36,'Al':1.18,'Si':1.11,'Ti':1.32,'V':1.22,
                'Cr':1.18,'Mn':1.17,'Fe':1.17,'Co':1.16,'Ni':1.15,'Cu':1.17,'Zn':1.25,'Ge':1.22,'Y':1.62,
                'Zr':1.45,'Nb':1.34,'Mo':1.30,'Ru':1.25,'Rh':1.25,'Pd':1.28,'Ag':1.34,'Sn':1.4,'Ce':1.65,
                'Nd':1.64,'Hf':1.44,'Ta':1.34,'W':1.30,'Re':1.28,'Ir':1.27,'Pt':1.30,'Au':1.34}
    folds_file = 'tmp_folds.csv'
    expands_file = 'tmp_expands.csv'
    if isinstance(input,list):
        name = input
    elif isinstance(input,str):
        name = []
        name.append(input)
    splitter = NameSplit()
    splitter.transform(name,folds_name=folds_file,expands_name=expands_file)
    df = pd.read_csv(expands_file,index_col=0)
    first_cell = df.iloc[0,0]
    for i in range(0,len(df)):
        row_sum = df.iloc[i,1:].sum()
        if row_sum ==0:
           continue
        scaling_factor = 1/row_sum
        for j in range(1, len(df.columns)):
            df.iloc[i,j] = df.iloc[i,j] * scaling_factor
        df.iloc[0,0] = first_cell
    os.remove(folds_file)
    os.remove(expands_file)
    df = df[[col for col in df if col in VEC_dict]]
    elements = [col for col in df.columns]
    #VEC CALCULATION
    df['VEC'] = 0.0
    for index, row in df.iterrows():
        total_vec = 0.0
        for element in elements: 
            c_i = row[element]  
            vec_i = VEC_dict[element] 
            total_vec += c_i * vec_i
            df.at[index, "VEC"] = total_vec
    #CALCULATE DELTA
    df['delta(%)'] = 0.0
    Hmix_data = pd.read_csv(binary_Hmix_data_path, index_col=0)
    for index, row in df.iterrows():
        average_radius = sum(row[element] * radius_dict[element] for element in elements)
        delta_square = sum(row[element] * ((1 - (radius_dict[element] / average_radius)) ** 2) for element in elements)
        delta = math.sqrt(delta_square)
    #CALCULATE AND FILLIN Hmix, Smix, Lambda
        total_mixing_enthalpy = 0.0
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                element1 = elements[i]
                element2 = elements[j]
                c_1 = float(row[element1])
                c_2 = float(row[element2])
                binaryHmix = 0.0
                if (element1 == element2):
                    raise ValueError ('same element')
                elif (pd.notna(Hmix_data.loc[element1,element2])):
                    binaryHmix = Hmix_data.loc[element1,element2]
                else:
                    binaryHmix = Hmix_data.loc[element2,element1]
                total_mixing_enthalpy += 4*c_1*c_2*float(binaryHmix)
            total_mixing_entropy = 0.0
        for element in elements:
            if (row[element]> 0):
                total_mixing_entropy += -8.314*row[element]*math.log(row[element])  
            else:
                continue       
        df.at[index, "delta(%)"] = delta * 100
        df.at[index, "Hmix(kJ/mol)"] = total_mixing_enthalpy
        df.at[index, "Smix(J/Kmol)"] = total_mixing_entropy
        df.at[index, "Lambda"] = total_mixing_entropy /(delta*100)**2
    return df

def Rules_check(input_csv):
    if isinstance(input_csv, str):
        df = pd.read_csv(input_csv)
    else:
        df = input_csv
    # Hmix-δ判据
    conditions_Hmix_delta = [
        (df["delta(%)"] < 6.66) & (df["Hmix(kJ/mol)"] < 6.92),        # Class SS
        (df["delta(%)"] > 5.64) & (df["Hmix(kJ/mol)"] < -20.0),      # Class Non-Crystal
        ~((df["delta(%)"] < 6.66) & (df["Hmix(kJ/mol)"] < 6.92)) & ~((df["delta(%)"] >5.64) & (df["Hmix(kJ/mol)"] <-20.0))  # Class compounds
    ]
    choices_Hmix_delta = [0, 1, 2]
    df["Hmix_delta"] = pd.Series(
        np.select(conditions_Hmix_delta, choices_Hmix_delta, default=0),  # default=0 表示未匹配的归为 0
        dtype=int)
    # Ω-δ判据
    
    conditions_Omega_delta = [
        (df["Omega"] >= 1.1) & (df["delta(%)"] <= 0.066),        # Class SS
        ~ ((df["Omega"] >= 1.1) & (df["delta(%)"] <= 0.066)) # Class Non-SS
    ]
    choices_Omega_delta = [0, 1]
    df["Omega_delta"] = pd.Series(
        np.select(conditions_Omega_delta, choices_Omega_delta, default=0),  # default=0 表示未匹配的归为 0
        dtype=int)
    # λ判据
    conditions_Lambda = [
        (df["Lambda"] > 0.245),        # Class disorder SS
        ~ (df["Lambda"] > 0.245)       # Class Non-SS
    ]
    choices_Lambda = [0, 1] 
    df["Lambda_rule"] = pd.Series(
        np.select(conditions_Lambda, choices_Lambda, default=0),  # default=0 表示未匹配的归为 0
        dtype=int)
    # VEC判据
    conditions_VEC = [
        (df["VEC"] >= 2.909),         # Class FCC
        (df["VEC"] < 0.5),         # Class BCC
        (df["VEC"] >= 0.5) & (df["VEC"] < 2.909), #Class FCC+BCC
    ]
    choices_VEC = [0, 1, 2] 
    df["VEC_rule"] = pd.Series(
        np.select(conditions_VEC, choices_VEC, default=0),  # default=0 表示未匹配的归为 0
        dtype=int)
    # δ判据
    conditions_delta = [
        (df["delta(%)"] > 7.44),    # Class compounds
        (df["delta(%)"] <= 7.44) & (df["delta(%)"]>= 3)         # Class BCC
    ]
    choices_delta = [0, 1] 
    df["delta_rule"] = pd.Series(
        np.select(conditions_delta, choices_delta, default=0),  # default=0 表示未匹配的归为 0
        dtype=int)
    return df 


if __name__ == "__main__":
    HEA_calculate()   
