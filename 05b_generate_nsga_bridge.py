
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



def do_hc(mcm = 1, rnd = 10000, p_size=200, q_size = 100, mutation_rate=0.1):

    regressors = pd.read_pickle("reg/best_s1.pkl.gz")
    start = time.time()
    from dctconf import MCM_configs, DCT_config

    config = {**DCT_config, **MCM_configs[f"mcm_c{mcm}"]}



    #print(config)

    regname_hw = regressors.loc[(mcm, "power"), "regname"]
    regname_qual = regressors.loc[(mcm, "total_psnr_yuv"), "regname"]
        
    reg_hw_p = f"reg/bridge-regressor.{regname_hw}.mcm{mcm}_power.joblib"
    reg_qual_p = f"reg/bridge-regressor.{regname_qual}.mcm{mcm}_total_psnr_yuv.joblib"

    reg_hw = joblib.load(reg_hw_p)
    reg_qual = joblib.load(reg_qual_p)

    # loading library
    lib = pd.read_pickle("components/data/circ.lib.pkl.gz")
    #library = json.load(open("../adders/library.json")) # without params


    lib_ct =  {
        ct: list(d["cfun"])
        for ct, d in lib.groupby("circ_type")
    }
    print(lib_ct)
   

    lib_hw_vals = {x: [y] for x,y in lib.set_index("cfun")[["fpga_power"]].itertuples()}
    lib_qual_vals = {x: [y, z] for x,y,z in lib.set_index("cfun")[["bddavg", "bddmax"]].itertuples()}

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
            X_hw.append([y for x in parameters for y in lib_hw_vals[o["conf"][x]]])
            X_qual.append([y for x in parameters for y in lib_qual_vals[o["conf"][x]]])


        y_hw = reg_hw.predict(X_hw)
        y_qual = reg_qual.predict(X_qual)


        return [{"conf": c["conf"], "est_hw": h, "est_qual": q} for c, h, q in zip(population, y_hw, y_qual)]
        
    
    def crowding_distance(par, objs):
        """ calculates crowding distance for pareto frontier par for objectives objs """
        park = list(zip(range(len(par)), par)) # list of "ids, evaluated_offsprint"
        distance = [0 for _ in range(len(par))]

        for o in objs:
            sval = sorted(park, key=lambda x: x[1][o]) # sort by objective
            minval, maxval = sval[0][1][o], sval[-1][1][o]
            # distance of the lowest and highest value is infty
            distance[sval[0][0]] = float("inf")
            distance[sval[-1][0]] = float("inf") 

            for i in range(1, len(sval) - 1):
                distance[sval[i][0]] += abs(sval[i - 1][1][o] - sval[i + 1][1][o]) / (maxval - minval)
    
        return zip(par, distance)

    def crowding_reduce(par, number, objs):
        """ Removes the elements from pareto frontier; iteratively removest the node with the lowest crowding distance """
        par = par
        while len(par) > number:
            vals = crowding_distance(par, objs)
            vals = sorted(vals, key = lambda x: -x[1]) # sort by distance descending
            #print(vals)

            par = [x[0] for x in vals[:-1]]
        return par
        

    # Generate random configurations
    parent = [random_conf(config) for _ in range(p_size)]
    parameters = sorted(config)

    alld = []

    parent = evaluate_population(parent)

    #print(json.dumps(parent, indent=2))
    
    metrics = ["est_hw", "est_qual"]

    import matplotlib.pyplot as plt

    for rid in tqdm(range(rnd), f"NSGA search mcm={mcm}"):
        
        offsprings = [mutate_conf(
            crossover_conf(random.choice(parent), random.choice(parent), config), 
            config, random.random() < mutation_rate) for _ in range(q_size)]


        offsprings = evaluate_population(offsprings)
        population = parent + offsprings

        # selection of pareto frontiers
        next_parent = []
        while len(next_parent) < p_size:
            # select pareto frontier
            pareto = PyBspTreeArchive(len(metrics), minimizeObjective1=True, minimizeObjective2=False).filter([[x[m] for m in metrics] for x in population], returnIds=True)

            current_pareto = [population[i] for i in pareto]
            missing = p_size - len(next_parent)

            if(len(current_pareto) <= missing): # can we put all pareto frontier to the next parent
                next_parent += current_pareto
            else: # distance crowding 
                next_parent += crowding_reduce(current_pareto, missing, metrics)

            for i in reversed(sorted(pareto)): # delete nodes from the current population
                population.pop(i)

        #print(json.dumps(next_parent, indent=2))

        parent = next_parent
        if rid % (rnd / 10) == 0:
            plt.figure()
            
            df = pd.DataFrame(parent)
            df.to_pickle(f"data/bridge-nsga_mcm{mcm}_{rnd}x{p_size}_gen_{rid}.pkl.gz")

            plt.scatter(df["est_hw"], df["est_qual"])
            plt.xlim(0, None)
            plt.ylim(0, None)
            plt.savefig(f"data/bridge-nsga_mcm{mcm}_{rnd}x{p_size}_gen_{rid}.png")
            plt.close()
            
            #plt.show()
        #if rid == 100: break
        #xxxxx

    print("Run done ...")
    print()
    print("Filt pareto combinations: %d in %f seconds" % (len(next_parent), time.time() - start))
    sl = [cid2p[cid] for cid in pf.points(returnIds=True)]  
    alld = pd.DataFrame(alld)


    outc = {}
    for x in parent:
        while True:
            cid = f"nsga_bridge_mcm{mcm}_" + uuid1().hex[:8].upper()
            if not cid in outc:
                break
            print(cid, cid in outc)

        x["conf"]["mcm"] = mcm

        assert cid not in outc
        outc[cid]= x["conf"]

    json.dump(outc, gzip.open(f"configs/bridge-nsga_mcm{mcm}_{rnd}x{p_size}.json.gz", "wt"), indent=2)
    pd.DataFrame(sl).to_pickle(f"data/bridge-nsga_mcm{mcm}_{rnd}x{p_size}.pkl.gz")
    #xxxx


if __name__ == "__main__":
    for mcm in [1, 2, 3, 4]:
        do_hc(mcm = mcm)
    #do_hc(circ = "HPF", metr = "temp_psnr")
    #do_hc(circ = "DER", metr = "temp_psnr")
    #do_hc(circ = "SWI", metr = "beats")
    #do_hc(circ = "all", metr = "beats")
# %%
