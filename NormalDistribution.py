import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_excel('./AutoData.xlsx', usecols=[0], names=None)
df_li = df.values.tolist()
result = []
for s_li in df_li:
    result.append(s_li[0])
datas = np.array(result)

mu = np.mean(datas)
sigma = np.std(datas, ddof=1)


nums, bins, patches = plt.hist(datas, bins=35, rwidth=0.6, density=True)
bin = list(map(int, bins[:]))
# bin = np.trunc(bins)
plt.xticks(bin,bin)


x = np.arange(min(datas), max(datas),0.1)
y = np.exp(-((x-mu)**2)/(2*sigma**2))/(sigma*np.sqrt(2*np.pi))

ci = stats.norm.interval(0.99, loc=mu, scale=sigma)
print(ci)
plt.plot(x,y)
plt.show()
