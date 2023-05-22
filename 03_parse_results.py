#%%
import components.fpgaparser as fp
import pandas as pd
# %%
res_fpga_random = fp.parse_zip_file("data/verilog_random_FPGA_results.zip")
res_fpga_random
# %%
res_fpga_accurate = fp.parse_zip_file("data/verilog_accurate_FPGA_results.zip")
res_fpga_accurate
# %%
df_fpga = pd.DataFrame.from_dict({**res_fpga_random, **res_fpga_accurate}, orient="index").dropna(subset=["power", "delay"])
df_fpga
# %%
import gzip, json
res_eval = json.load(gzip.open("data/eval.jsn.gz"))
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
# %%

df_conf = pd.read_json("configs/random.json.gz", orient="index")
df_t = pd.merge(df_conf, df_fpga, left_index=True, right_index=True)
df_t["configuration"] = df_t.index
df_random = pd.merge(df_t, df_res, on="configuration")
df_random
# %%
df_random.to_pickle("data/all_random.pkl.gz")
# %%
df_conf = pd.read_json("configs/accurate.json.gz", orient="index")
df_t = pd.merge(df_conf, df_fpga, left_index=True, right_index=True)
df_t["configuration"] = df_t.index
df_accurate = pd.merge(df_t, df_res, on="configuration")
df_accurate
# %%
df_accurate.to_pickle("data/all_accurate.pkl.gz")

# %%
import seaborn as sns
# %%

df_random["type"] = "random"
df_accurate["type"] = "accurate"
df = pd.concat([df_random, df_accurate])

sns.relplot(data = df.query("qp==37"),
            hue="mcm",
            x="power",
            y="bslice_psnr_yuv_median",
            style="type",
            palette="tab10",
            col="benchmark", facet_kws=dict(sharey=False))
# %%
