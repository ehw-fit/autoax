#%%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


#%%


data_wo = pd.read_pickle("reg/bridge-corr_random.pkl.gz")
data_wo["corr"] = data_wo["corr"].astype("f")

data = pd.read_pickle("reg/bridge-abc-corr_random.pkl.gz")
data["corr"] = data["corr"].astype("f")
data

#%%
#%%
sns.factorplot(data=data,
        kind="bar", x="regname", y="corr", hue="kind",
        col="mcm", row="y_param")

plt.savefig("plt/bridge-abc-regression_first.png")
plt.show()

#%%
test_data = data.query("kind=='test'")

test_data.set_index(["mcm", "y_param"], inplace=True)

mvals = test_data.groupby(["mcm", "y_param"], sort=False)["corr"].agg("max")
test_data["maxcorr"] = mvals
#%%

df = test_data[test_data["corr"] == test_data["maxcorr"]][["regname"]]
df.to_pickle("reg/bridge-abc-best_s1.pkl.gz")
df

# %%
data_wo["abc"] = False
data["abc"] = True

test_data = pd.concat([data, data_wo]).query("kind=='test' and y_param=='power'")

df_comp = test_data.groupby(["mcm", "y_param", "abc"]).agg({"corr": "max"}).reset_index()
print(df_comp.to_markdown(index=False))


# %%

df_a = df_comp.pivot(["mcm", "y_param"], ["abc"], ["corr"])
df_a["improvement"] = df_a[("corr",True)] - df_a[("corr",False)]
print(df_a.reset_index().to_markdown(index=False))
# %%

df_a[("corr", True )].mean(), df_a[("corr", False)].mean(), df_a["improvement"].mean()
# %%
