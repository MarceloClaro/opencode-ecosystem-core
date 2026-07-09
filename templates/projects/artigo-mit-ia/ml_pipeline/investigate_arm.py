import pandas as pd, numpy as np

df = pd.read_csv('outputs/dataset_latest.csv')
print('Shape:', df.shape)
print('ARM count:', df['arm_trapped'].value_counts().to_dict())

arm1 = df[df['arm_trapped'] == 1]
print('\nARM=1 countries:')
print(arm1[['economy', 'year']].to_string(index=False))

print('\nNaN per ARM country:')
features = ['gdp_per_capita','tertiary_enrollment','rd_spending','patent_apps',
            'high_tech_exp','internet_users','fdi_inflows','unemployment','gini',
            'services_emp','ai_readiness']

for _, row in arm1.iterrows():
    nulls = row[features].isna().sum()
    total = len(features)
    print(f'{row["economy"]}: {nulls}/{total} NaN')
    null_cols = row[features][row[features].isna()].index.tolist()
    if null_cols:
        print(f'  Missing: {null_cols}')

df2 = df.dropna(subset=features + ['arm_trapped'], how='any')
print(f'\nAfter dropna: {df2.shape}')
print(f'ARM=1 after dropna: {df2["arm_trapped"].sum()}')
