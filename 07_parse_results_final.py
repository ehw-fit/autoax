#%%
import components.fpgaparser as fp
import pandas as pd
import numpy as np
# %%
# Parse FPGA
alldf = []
for mcm in [1, 2, 3, 4]:
    df_f = pd.DataFrame.from_dict(
        fp.parse_zip_file(f"data/verilog_nsga_mcm{mcm}_FPGA.zip"),
        orient="index").dropna(subset=["power", "delay"])
    alldf.append(df_f)
df_fpga = pd.concat(alldf)
df_fpga
# %%
# %%
import gzip, json
res_eval = json.load(gzip.open("data/eval_final.jsn.gz"))
res_eval

# %%
alld = []
for e in res_eval:
    r = {}

    for k, v in e.items():
        if type(v) is dict:
            kn = k.replace("result_", "")
            r = {**r, **{f"{kn}_{k2}": v2    for k2, v2 in v.items()}}
        else:
            r[k] = v
    alld.append(r)

df_res = pd.DataFrame(alld)
df_res
# %%

alldf = []
for mcm in [1, 2, 3, 4]:
    alldf.append(pd.read_json(f"configs/nsga_mcm{mcm}_10000x200.json.gz", orient="index"))
df_conf = pd.concat(alldf)
df_conf

# %%%
df_t = pd.merge(df_conf, df_fpga, left_index=True, right_index=True)
df_t["configuration"] = df_t.index
df = pd.merge(df_t, df_res, on="configuration").dropna(subset=["power"])
df
# %%
df.to_pickle("data/all_final.pkl.gz")
df_final = df.copy()
# %%%
# %%
import seaborn as sns
# %%
df_random = pd.read_pickle("data/all_random.pkl.gz")
df_accurate = pd.read_pickle("data/all_accurate.pkl.gz")

#%%%
df_random["type"] = "random"
df_accurate["type"] = "accurate"
df_final["type"] = "final"
df = pd.concat([df_random, df_accurate, df_final])

sns.relplot(data = df.query("qp==37"),
            hue="mcm",
            row="type",
            x="power",
            y="total_psnr_yuv",
            style="type",
            palette="tab10",
            col="benchmark", facet_kws=dict(sharey=True))
# %%
def issame(x):
    #print(x)
    first = x.iloc[0]
    if np.all(x == first):
        return first
    return None
aggf = {x: issame if x == "mcm" or df[x].dtype == np.dtype("O") else "mean" for x in df.columns}

sns.relplot(data = df.query("qp==37").groupby("configuration").agg(aggf),
            hue="mcm",
            col="type",
            x="power",
            y="total_psnr_yuv",
            palette="tab10",
            facet_kws=dict(sharey=True))
# %%
