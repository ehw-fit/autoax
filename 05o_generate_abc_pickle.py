
#%%%
from re import X
import joblib
from tqdm import tqdm
from paretoarchive import PyBspTreeArchive
import pandas as pd
import numpy as np
import json
import random
import time
import gzip
from uuid import uuid1
from abcsynth import ABCsynth


def generate_pickle(mcm = 1, ):

    abc = ABCsynth()
    
    regressors = pd.read_pickle("reg/bridge-abc-best_s1.pkl.gz")
    start = time.time()
    from dctconf import MCM_configs, DCT_config

    config = {**DCT_config, **MCM_configs[f"mcm_c{mcm}"]}



    #print(config)

    regname_hw = regressors.loc[(mcm, "power"), "regname"]
    regname_qual = regressors.loc[(mcm, "total_psnr_yuv"), "regname"]
        
    reg_hw_p = f"reg/bridge-abcregressor.{regname_hw}.mcm{mcm}_power.joblib"
    reg_qual_p = f"reg/bridge-abcregressor.{regname_qual}.mcm{mcm}_total_psnr_yuv.joblib"

    reg_hw = joblib.load(reg_hw_p)
    reg_qual = joblib.load(reg_qual_p)

    # loading library
    df_lib = pd.read_pickle("components/data/circ.lib.pkl.gz")
    df_abc = pd.read_pickle("components/data/circ.abc.pkl.gz")
    lib = pd.merge(df_lib, df_abc[["file", "abc_power"]], on="file")

    lib_ct =  {
        ct: list(d["cfun"])
        for ct, d in lib.groupby("circ_type")
    }
    
    qual_params = ["bddavg", "bddmax"]

    lib_hw_vals = {x: [y] for x,y in lib.set_index("cfun")[["abc_power"]].itertuples()}
    lib_qual_vals = {x: [y, z] for x,y,z in lib.set_index("cfun")[qual_params].itertuples()}
    abc_params=["abc_lat", "abc_nd", "abc_edge", "abc_aig", "abc_lev", "abc_power"]

    pf = PyBspTreeArchive(2, minimizeObjective1=True, minimizeObjective2=True)
    cid2p = {}
    starvation = 0

    #P, Q = (1000, 1000)



    def mutate_conf(x, config, do_mutate = True):
        if not do_mutate: 
            return x.copy()
        c = {"conf": x["conf"].copy()}
        #print(c)
        j = random.choice(list(config))
        c["conf"][j] = random.choice(lib_ct[config[j]])
        return c
        

    def crossover_conf(x, y, config):
        #print(random.choice([x, y]))
        return {
            "conf": {
                p: random.choice([x, y])["conf"][p] for p in config
            }

        }

    def random_conf(config):
        return {    
                "conf": {
                    j: random.choice(lib_ct[config[j]]) for j in config
                }
            }

    def evaluate_population(population):
        X_hw = []
        X_qual = []
        for o in population:

            hw_x = {x + "_abc_power": y for x in parameters for y in lib_hw_vals[o["conf"][x]]}

            if abc_params:
                r_abc = abc.runSynth({"mcm":mcm, **(o["conf"])})
                hw_x = {**hw_x, **{i: r_abc[i] for i in abc_params}}
            X_hw.append(hw_x)
            X_qual.append({x + "_" + y_n: y for x in parameters for y_n, y in zip(qual_params, lib_qual_vals[o["conf"][x]])})

        X_hw = pd.DataFrame(X_hw)[reg_hw.feature_names_in_]
        X_qual = pd.DataFrame(X_qual)[reg_qual.feature_names_in_]
        #print(X_qual)
        #print(reg_qual.feature_names_in_)
        y_hw = reg_hw.predict(X_hw)
        y_qual = reg_qual.predict(X_qual)


        return [{"conf": c["conf"], "est_hw": h, "est_qual": q} for c, h, q in zip(population, y_hw, y_qual)]


    parameters = sorted(config)
    # Generate random configurations
    outc = json.load(gzip.open(f"configs/bridge-abc-nsga_mcm{mcm}_1000x200.json.gz", "rt"))


    parent = []
    ks = []
    for k in outc.keys():
        
        del outc[k]["mcm"]
        parent.append({"conf": outc[k]})
        ks.append(k)

    alld = []



    parent = evaluate_population(parent)


    outc = {}
    for cid, x in zip(ks, parent):
        x["conf"]["mcm"] = mcm

        assert cid not in outc
        outc[cid]= x["conf"]

    #json.dump(outc, gzip.open(f"configs/bridge-abc-nsga_mcm{mcm}_{rnd}x{p_size}.json.gz", "wt"), indent=2)
    pd.DataFrame(parent).to_pickle(f"data/bridge-abc-nsga_mcm{mcm}_1000x200.pkl.gz")
    #xxxx
    print(pd.DataFrame(parent))


if __name__ == "__main__":
    for mcm in [1, 2, 3, 4]:
       generate_pickle(mcm=mcm)
    #do_hc(circ = "HPF", metr = "temp_psnr")
    #do_hc(circ = "DER", metr = "temp_psnr")
    #do_hc(circ = "SWI", metr = "beats")
    #do_hc(circ = "all", metr = "beats")
# %%
