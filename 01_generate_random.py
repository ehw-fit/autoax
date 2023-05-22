"""
Create random assignments
"""
#%%
from itertools import product
import pandas as pd
import numpy as np
from dctconf import MCM_configs, DCT_config

df_lib = pd.read_pickle("components/data/circ.lib.pkl.gz")


MCMs = list(MCM_configs.keys())


#%%
# Count possible combinations

df_lib = pd.read_pickle("components/data/circ.lib.pkl.gz")

#df_lib["circ_type"] = df_lib["file"].apply(lambda x: x.split("/")[1])
#df_lib["cfun"] = "xxx"

#%%

def get_possible(df, circ_type):
    c = list(df.query("circ_type == @circ_type")["cfun"])
    #print("# ", circ_type, len(c))
    if not len(c): 
        print("missing", circ_type)
        return "nan"
    return c

# DCT
cnt = 1
types = []
possible = {}
for _, v in DCT_config.items():
    possible[v] = get_possible(df_lib, v)
    cnt *= len(possible[v])
    types.append(v)


print("DCT confs: ", cnt)

for m, ms in MCM_configs.items():
    cnt_m = 1
    for _, cv in ms.items():
        possible[cv] = get_possible(df_lib, cv)
        cnt_m *= len(possible[cv])
        types.append(cv)

    print(m, cnt_m)


#%%
# Generate random configs:
np.random.seed(42)
import uuid
configs = {}
for i in np.arange(5000):
    uid = "random_" + str(uuid.uuid4().hex[:6].upper())

    assert uid not in configs

    mcm = int(np.random.choice([1, 2, 3, 4]))
    
    r = {
        "mcm": mcm
    }

    for k, t in DCT_config.items():
        r[k] = np.random.choice(possible[t])

    for k, t in MCM_configs[f"mcm_c{mcm}"].items():
        r[k] = np.random.choice(possible[t])

    configs[uid] = r

import json, gzip
json.dump(configs, gzip.open("configs/random.json.gz", "wt"), indent=2)


#%%%
configs = {}
def get_accurate(pos):
    for k in pos:
        if k.endswith("_acc"): return k
    assert False

for mcm in [1, 2, 3, 4]:
    uid = f"accurate_mcm{mcm}"

    assert uid not in configs

    r = {
        "mcm": mcm
    }

    for k, t in DCT_config.items():
        r[k] = get_accurate(possible[t])

    for k, t in MCM_configs[f"mcm_c{mcm}"].items():
        r[k] = get_accurate(possible[t])

    configs[uid] = r

import json, gzip
json.dump(configs, gzip.open("configs/accurate.json.gz", "wt"), indent=2)

# %%
