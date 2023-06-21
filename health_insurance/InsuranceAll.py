import pickle

import pandas as pd

# limpezas, transformações e encodes
class InsuranceAll(object):
    def __init__(self):
        self.standard_scaler_annual_premium = pickle.load(open('parameter/standard_scaler_annual_premium.pkl', 'rb'))
        self.min_max_scaler_age             = pickle.load(open('parameter/min_max_scaler_age.pkl', 'rb'))
        self.min_max_scaler_vintage         = pickle.load(open('parameter/min_max_scaler_vintage.pkl', 'rb'))
        self.target_encode_region_code      = pickle.load(open('parameter/target_encode_region_code.pkl', 'rb'))
        self.fe_policy_sales_channel        = pickle.load(open('parameter/fe_policy_sales_channel.pkl', 'rb'))
        
    def data_cleaning(self, df1):
        # renomeando colunas
        cols_new = ['id', 'gender', 'age', 'driving_license', 'region_code', 'previously_insured', 'vehicle_age', 'vehicle_damage', 
                    'annual_premium', 'policy_sales_channel', 'vintage']
        
        df1.columns = cols_new
        
        return df1

    def feature_engineering(self, df2):
        # vehicle_age
        vehicle_age = {'< 1 Year': 'below_1_year', '1-2 Year': 'between_1_2_year', '> 2 Years': 'over_2_years'}
        df2['vehicle_age'] = df2['vehicle_age'].map(vehicle_age)
        
        return df2

    def data_preparation(self, df5):
        ## 5.1. Normalização
        # annual_premium
        df5['annual_premium'] = self.standard_scaler_annual_premium.transform(df5[['annual_premium']].values)

        ## 5.2. Redimensionando
        # age - MinMaxScaler
        df5['age'] = self.min_max_scaler_age.transform(df5[['age']].values)

        # vintage - MinMaxScaler
        df5['vintage'] = self.min_max_scaler_vintage.transform(df5[['vintage']].values)

        ## 5.3. Encoder
        # region_code - Target Encoding
        df5.loc[:, 'region_code'] = df5['region_code'].map(self.target_encode_region_code)

        # policy_sales_channel - Frequency Encoding
        df5.loc[:, 'policy_sales_channel'] = df5['policy_sales_channel'].map(self.fe_policy_sales_channel)

        # vehicle_age - One Hot Encoding
        df5 = pd.get_dummies(df5, prefix='vehicle_age', columns=['vehicle_age'], dtype='int64')

        # vehicle_damage - One Hot Encoding
        df5 = pd.get_dummies(df5, prefix='vehicle_damage', columns=['vehicle_damage'], dtype='int64')

        # gender - One Hot Encoding
        df5 = pd.get_dummies(df5, prefix='gender', columns=['gender'], dtype='int64')

        # colunas selecionadas
        cols_selected = ['age', 'region_code', 'previously_insured', 'annual_premium', 'policy_sales_channel', 
                         'vintage', 'vehicle_damage_No', 'vehicle_damage_Yes']
        
        # tratando o dataframe caso alguma coluna esteja ausente
        cols = []
        # separando as colunas ausentes
        for x in cols_selected:        
            if (x in df5.columns) == False:
                cols.append(x)        
        
        # adicionando colunas ausentes com valor 0
        if len(cols) != 0:
            for index, value in enumerate(cols):
                df5[value] = 0
        
        # fillna
        df5 = df5.fillna(0)
        
        return df5[cols_selected]

    def get_prediction(self, model, original_data, test_data):
        # modelo
        pred = model.predict_proba(test_data)
        
        # unir predição como dataset original
        original_data['score'] = pred
        
        return original_data.to_json(orient='records', date_format='iso')
