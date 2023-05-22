#%%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


#%%


data = pd.read_pickle("reg/corr_random.pkl.gz")

data["corr"] = data["corr"].astype("f")
data

#%%
#%%
sns.factorplot(data=data,
        kind="bar", x="regname", y="corr", hue="kind",
        col="mcm", row="y_param")

plt.savefig("plt/regression_first.png")
plt.show()

#%%
test_data = data.query("kind=='test'")

test_data.set_index(["mcm", "y_param"], inplace=True)

mvals = test_data.groupby(["mcm", "y_param"], sort=False)["corr"].agg("max")
test_data["maxcorr"] = mvals
#%%

df = test_data[test_data["corr"] == test_data["maxcorr"]][["regname"]]
df.to_pickle("reg/best_s1.pkl.gz")
df

# %%
