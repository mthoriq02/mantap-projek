import pandas as pd

data_raw = pd.read_excel('gun_repository.xlsx')
all_data = data_raw.to_dict(orient='records')