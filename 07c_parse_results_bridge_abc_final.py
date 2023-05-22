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
        fp.parse_zip_file(f"data/verilog_bridge_abc_nsga_mcm{mcm}_1000x200_FPGA.zip"),
        orient="index").dropna(subset=["power", "delay"])
    df_f["opt_meth"] = "nsga"
    alldf.append(df_f)

    df_f = pd.DataFrame.from_dict(
        fp.parse_zip_file(f"data/verilog_bridge_abc_hc_mcm{mcm}_1000_FPGA.zip"),
        orient="index").dropna(subset=["power", "delay"])
    df_f["opt_meth"] = "hc"
    alldf.append(df_f)
df_fpga = pd.concat(alldf)
df_fpga
# %%
# %%
res_eval = json.load(gzip.open("data/eval2.jsn.gz"))
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
        f"configs/bridge-abc-nsga_mcm{mcm}_1000x200.json.gz", orient="index"))
    alldf.append(pd.read_json(
        f"configs/bridge-abc-hc_mcm{mcm}_1000.json.gz", orient="index"))
df_conf = pd.concat(alldf)
df_conf
#
df_conf.index = df_conf.index.str.replace("abc-bridge", "abc_bridge")
df_conf
# %%%
df_t = pd.merge(df_conf, df_fpga, left_index=True, right_index=True)
df_t["configuration"] = df_t.index.str.replace("abc_bridge", "abc-bridge")
df = pd.merge(df_t, df_res, on="configuration").dropna(subset=["power"])
df
# %%
