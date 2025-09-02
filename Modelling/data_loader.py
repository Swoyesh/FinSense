import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

class DataLoader:
    def __init__(self, config):
        self.config = config

    def load_and_preprocess(self):
        df = pd.read_excel(self.config.excel_path, skiprows = self.config.skiprows)
        df = df.dropna()

        percentage = df.groupby('Category').size() / len(df)
        others_list = percentage[percentage < (self.config.category_threshold)].index.tolist()

        def new_func(x):
            return 'others' if x in others_list else x
        
        df = df['Category'].apply(lambda x: new_func(x))

        le = LabelEncoder()
        df['Category_encoded'] = le.fit_transform()
        self.label_to_id = {label: i for i, label in enumerate(le.classes_)}

        return df

