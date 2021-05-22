import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress

date = '2021-5-21'

aggregated_path = 'analysis/stage3/aggregated/{}-aggregated.csv'.format(date)


# ID,Domain,Mullvad Response Domain,Control Response Domain,Mullvad Status Code,Control Status Code,Mullvad Error,Control Error,PHash Difference

df = pd.read_csv (aggregated_path)
df[['Mullvad Status Code', 'Control Status Code']] = df[['Mullvad Status Code', 'Control Status Code']].fillna(0.0).astype(int)
# print(df)

# print(df.mean())

# x = list(df['Mullvad Status Code'].fillna(0.0).astype(int))
# y = list(df['Control Status Code'].fillna(0.0).astype(int))
# # plt.scatter(x, y)

# # Add x and y lables, and set their font size
# plt.xlabel("Mullvad Status Code", fontsize=10)
# plt.ylabel("Control Status Code", fontsize=10)

# plt.show()
