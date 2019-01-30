import pandas as pd

df = pd.read_csv('data/politiek/handelingen/all-handelingen.csv')
print(df.columns)
print(len(df))
li_vergaderingen = set(df['item-titel-full'].tolist())
#print(li_vergaderingen)
print(len(li_vergaderingen))
li_sprekers = set(df['spreker'].tolist())
#print(li_sprekers[:5])
print(len(li_sprekers))