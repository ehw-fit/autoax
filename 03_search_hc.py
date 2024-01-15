
# %%%
import argparse
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
from autoax import Config, FeatureExtractor


def do_hc(config, variant, iterations=10000, population=100, seed=None, result_file = None):
    # load config and items
    c = Config(config)

    variant_data = c.get_variant(variant)
    libraries = c.components()

    items = c.components_keys()

    # find the best regressor
    df_quality = pd.read_pickle(c.result_path(
        f"models_{variant}/quality.pkl.gz"))
    models = {}
    objective = {}
    fe = {}
    if not result_file:
        result_file = c.block_on_result(f"hc_{variant}.json.gz")

    for obj in ["hw", "qor"]:
        df_q = df_quality.query("objective == @obj")
        # print(df_q)
        sel = df_q.iloc[df_q.test_score.argmax()]
        print("# Selected model for ", obj, " is ", sel.model)
        models[obj] = joblib.load(c.result_path(
            f"models_{variant}/{obj}.{sel.model}.joblib"))

        # Prepare feature extractor

        ft = variant_data["features"]
        features = ft[obj] if obj in ft else []
        features_glob = ft[obj + "glob"] if obj + "glob" in ft else []
        objective[obj] = variant_data["objectives"][obj]

        assert (len(features) + len(features_glob) > 0)

        # Prepare features
        fe[obj] = FeatureExtractor(c, modules=variant_data["modules"])
        fe[obj].setFeatures(features)
        fe[obj].setFeaturesGlobal(features_glob)

    def random_conf():
        # Generate random configuration
        r = {}
        for k, library in libraries.items():
            r[k] = random.choice(library.possible())
        return r

    def mutate_conf(x, do_mutate=True):
        if not do_mutate:
            return x.copy()
        c = x.copy()
        j = random.choice(items)
        c[j] = random.choice(libraries[j].possible())
        if "est_hw" in c:
            del (c["est_hw"])
        if "est_qor" in c:
            del (c["est_qor"])
        return c

    def evaluate_population(population):
        # print(population)

        X_hw = []
        X_qor = []
        for p in population:
            X_hw.append(fe["hw"](p))
            X_qor.append(fe["qor"](p))

        # print(pd.DataFrame(X_hw))
        est_hw = models["hw"].predict(pd.DataFrame(X_hw))
        # print(pd.DataFrame(X_qor))
        est_qor = models["qor"].predict(pd.DataFrame(X_qor))

        for i, p in enumerate(population):
            p["est_hw"] = est_hw[i]
            p["est_qor"] = est_qor[i]
        return population
    
    if seed:
        random.seed(seed)

    parent = random_conf()

    pf = PyBspTreeArchive(2, minimizeObjective1=True, minimizeObjective2=False)
    cid2p = {}
    starvation = 0

    start = time.time()
    for rid in tqdm(range(iterations), f"HC search "):

        offsprings = [mutate_conf(parent) for _ in range(population)]

        offsprings = evaluate_population(offsprings)

        for o in offsprings:
            dom, cid = pf.process([o["est_hw"], o["est_qor"]], returnId=True)

            if dom:
                cid2p[cid] = o
                parent = o
                #print("\rConf: %d (%.3f %%), ndom = %d" %
                #      (rid, 100.0 * rid / iterations, pf.size()), end="")
                # starvation_all.append(starvation)
                starvation = 0

            else:
                starvation += 1
                if starvation > 50:
                    sl = [cid2p[cid] for cid in pf.points(returnIds=True)]
                    parent = sl[random.randint(0, len(sl)-1)]
    print("Run done ...")
    print()
    print("Filt pareto combinations: %d in %f seconds" %
          (pf.size(), time.time() - start))
    print(f"Stored to {result_file}")
    sl = [cid2p[cid] for cid in pf.points(returnIds=True)]

    outc = {}
    for x in sl:
        while True:
            cid = f"hc_{variant}_" + uuid1().hex[:8].upper()
            if not cid in outc:
                break
            print(cid, cid in outc)

        assert cid not in outc
        outc[cid] = x.copy()

    json.dump(outc, gzip.open(result_file, "wt"), indent=2)
   


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('config', help='Config file (yaml)')
    p.add_argument('variant', help='Variant (from config file)')
    p.add_argument('--iterations', help='Number of iterations',
                   type=int, default=10000)
    p.add_argument('--population', help='Population size',
                   type=int, default=100)

    p.add_argument("--seed", help="Random seed", type=int, default=None)
    args = p.parse_args()
    do_hc(**vars(args))
# %%
