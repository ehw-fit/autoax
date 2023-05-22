# %%
import json
import gzip
from paretoarchive.pandas import pareto
import seaborn as sns
import components.fpgaparser as fp
import pandas as pd
import numpy as np
# %%
# Parse FPGA
alldf = []
for mcm in [1, 2, 3, 4]:
    df_f = pd.DataFrame.from_dict(
        fp.parse_zip_file(f"data/verilog_bridge_nsga_mcm{mcm}_FPGA.zip"),
        orient="index").dropna(subset=["power", "delay"])
    alldf.append(df_f)
df_fpga = pd.concat(alldf)
df_fpga
# %%
# %%
res_eval = json.load(gzip.open("data/eval_bridge.jsn.gz"))
res_eval

# %%
alld = []
for e in res_eval:
    r = {}

    for k, v in e.items():
        if type(v) is dict:
            kn = k.replace("result_", "")
            r = {**r, **{f"{kn}_{k2}": v2 for k2, v2 in v.items()}}
        else:
            r[k] = v
    alld.append(r)

df_res = pd.DataFrame(alld)
df_res
# %%

alldf = []
for mcm in [1, 2, 3, 4]:
    alldf.append(pd.read_json(
        f"configs/bridge-nsga_mcm{mcm}_10000x200.json.gz", orient="index"))
df_conf = pd.concat(alldf)
df_conf

# %%%
df_t = pd.merge(df_conf, df_fpga, left_index=True, right_index=True)
df_t["configuration"] = df_t.index
df = pd.merge(df_t, df_res, on="configuration").dropna(subset=["power"])
df
# %%
df.to_pickle("data/all_bridge_final.pkl.gz")
df_final = df.copy()
# %%%
# %%
# %%
df_random = pd.read_pickle("data/all_random.pkl.gz")
df_accurate = pd.read_pickle("data/all_accurate.pkl.gz")

# %%%
df_random["type"] = "random"
df_accurate["type"] = "accurate"
df_final["type"] = "final_bridge"

selection = "qp==37 and benchmark=='bridge-close'"
df = pd.concat([
    df_random.query(selection).sample(800, random_state=42),
    df_accurate.query(selection),
    df_final.query(selection)])

sns.relplot(data=df,
            hue="mcm",
            col="type",
            x="power",
            y="total_psnr_yuv",
            style="type",
            palette="tab10",
            # col="benchmark",
            facet_kws=dict(sharey=True))

# %%
# %%

alld = []
for d in [df_random.query(selection).sample(800, random_state=42),
          df_accurate.query(selection),
          df_final.query(selection)]:

    for mcm, dmcm in d.groupby("mcm"):
        alld.append(pareto(dmcm, ["power", "total_psnr_yuv"], minimizeObjective2=False))

df = pd.concat(alld)
g = sns.relplot(data=df,
    kind="line",
            hue="mcm",
            x="power",
            y="total_psnr_yuv",
            style="type",
            palette="tab10",
            marker="o",
            # col="benchmark",
            facet_kws=dict(sharey=True))
g.set(title="Pareto optimal solutions")
# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
alld = []
fig, ax = plt.subplots(1, 1, figsize=(7, 6))
for d in [df_random.query(selection).sample(800, random_state=42),
          df_accurate.query(selection),
          df_final.query(selection)]:

    if d.type.iloc[0] == "accurate":
        df_s = d.copy()
    else:
        df_s = pareto(d, ["power", "total_psnr_yuv"], minimizeObjective2=False)

    df_s = df_s.sort_values("power")

    ax.scatter(
        d["power"], d["total_psnr_yuv"],
        s = 5, alpha=0.4
    )

    ax.step(

        df_s["power"], df_s["total_psnr_yuv"],
        where="post",
        marker="o",
        label=d["type"].iloc[0]
    )
    
ax.legend()
ax.set(
    title="All MCMs",
    xlabel="Power",
    ylabel="PSNR YUV",
)
# %%
