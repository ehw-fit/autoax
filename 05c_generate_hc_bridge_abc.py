
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


def do_hc(mcm = 1, rnd = 10000, offc = 100, mutation_rate=0.1):

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
    print(dir(reg_hw))
    print(reg_hw.get_params())
    reg_qual = joblib.load(reg_qual_p)

    # loading library
    df_lib = pd.read_pickle("components/data/circ.lib.pkl.gz")
    df_abc = pd.read_pickle("components/data/circ.abc.pkl.gz")
    lib = pd.merge(df_lib, df_abc[["file", "abc_power"]], on="file")

    lib_ct =  {
        ct: list(d["cfun"])
        for ct, d in lib.groupby("circ_type")
    }
    print(lib_ct)
    
    qual_params = ["bddavg", "bddmax"]

    lib_hw_vals = {x: [y] for x,y in lib.set_index("cfun")[["abc_power"]].itertuples()}
    lib_qual_vals = {x: [y, z] for x,y,z in lib.set_index("cfun")[qual_params].itertuples()}
    abc_params=["abc_lat", "abc_nd", "abc_edge", "abc_aig", "abc_lev", "abc_power"]

    pf = PyBspTreeArchive(2, minimizeObjective1=True, minimizeObjective2=False)
    cid2p = {}
    starvation = 0


    def mutate_conf(x, config, do_mutate = True):
        if not do_mutate: 
            return x.copy()
        c = {"conf": x["conf"].copy()}
        #print(c)
        j = random.choice(list(config))
        c["conf"][j] = random.choice(lib_ct[config[j]])
        return c
        
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

    # Generate random configurations
    parent = random_conf(config)
    parameters = sorted(config)

    alld = []

    metrics = ["est_hw", "est_qual"]

    import matplotlib.pyplot as plt

    for rid in tqdm(range(rnd), f"HC search mcm={mcm}"):
        
        offsprings =  [mutate_conf(parent, config) for _ in range(offc)]

        offsprings = evaluate_population(offsprings)
        
        for o in offsprings:
            dom, cid = pf.process([o["est_hw"], o["est_qual"]], returnId = True)

            if dom:
                cid2p[cid] = o
                parent = o
                print("\rConf: %d (%.3f %%), ndom = %d" % (rid, 100.0 * rid / rnd, pf.size()), end="")
                #starvation_all.append(starvation)
                starvation = 0

            else:
                starvation += 1
                if starvation > 50:
                    sl = [cid2p[cid] for cid in pf.points(returnIds=True)]  
                    parent = sl[random.randint(0, len(sl)-1)]
    print("Run done ...")
    print()
    print("Filt pareto combinations: %d in %f seconds" % (pf.size(), time.time() - start))
    sl = [cid2p[cid] for cid in pf.points(returnIds=True)]  
    alld = pd.DataFrame(alld)


    outc = {}
    for x in sl:
        while True:
            cid = f"hc_abc-bridge_mcm{mcm}_" + uuid1().hex[:8].upper()
            if not cid in outc:
                break
            print(cid, cid in outc)

        x["conf"]["mcm"] = mcm

        assert cid not in outc
        outc[cid]= x["conf"]

    json.dump(outc, gzip.open(f"configs/bridge-abc-hc_mcm{mcm}_{rnd}.json.gz", "wt"), indent=2)
    pd.DataFrame(sl).to_pickle(f"data/bridge-abc-hc_mcm{mcm}_{rnd}.pkl.gz")
    #xxxx


if __name__ == "__main__":
    for mcm in [1, 2, 3, 4]:
        do_hc(mcm = mcm, rnd=1000)
    #do_hc(circ = "HPF", metr = "temp_psnr")
    #do_hc(circ = "DER", metr = "temp_psnr")
    #do_hc(circ = "SWI", metr = "beats")
    #do_hc(circ = "all", metr = "beats")
# %%
