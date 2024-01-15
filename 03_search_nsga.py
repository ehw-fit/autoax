
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


def do_nsga(config, variant, iterations=10000, p_size=200, q_size=100, mutation_rate=0.1, result_file=None, seed=None, **kwargs):
    # load config and items
    c = Config(config)

    variant_data = c.get_variant(variant)

    elements = json.load(gzip.open(c.result_path("random.eval.json.gz"), "rt"))
    libraries = c.components()

    items = c.components_keys()

    # find the best regressor
    df_quality = pd.read_pickle(c.result_path(
        f"models_{variant}/quality.pkl.gz"))
    models = {}
    objective = {}
    fe = {}

    if not result_file:
        result_file = c.block_on_result(f"nsga_{variant}.json.gz")

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

    def crossover_conf(a, b):
        c = {}
        for k in items:
            c[k] = random.choice([a, b])[k]
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

    def crowding_distance(par, objs):
        """ calculates crowding distance for pareto frontier par for objectives objs """
        park = list(zip(range(len(par)), par)
                    )  # list of "ids, evaluated_offsprint"
        distance = [0 for _ in range(len(par))]

        for o in objs:
            sval = sorted(park, key=lambda x: x[1][o])  # sort by objective
            minval, maxval = sval[0][1][o], sval[-1][1][o]
            # distance of the lowest and highest value is infty
            distance[sval[0][0]] = float("inf")
            distance[sval[-1][0]] = float("inf")

            for i in range(1, len(sval) - 1):
                distance[sval[i][0]] += abs(sval[i - 1][1]
                                            [o] - sval[i + 1][1][o]) / (maxval - minval)

        return zip(par, distance)

    def crowding_reduce(par, number, objs):
        """ Removes the elements from pareto frontier; iteratively removest the node with the lowest crowding distance """
        par = par
        while len(par) > number:
            vals = crowding_distance(par, objs)
            # sort by distance descending
            vals = sorted(vals, key=lambda x: -x[1])
            # print(vals)

            par = [x[0] for x in vals[:-1]]
        return par

    if seed:
        random.seed(seed)

    # Generate random configurations
    parent = [random_conf() for _ in range(p_size)]
    parent = evaluate_population(parent)

    metrics = ["est_hw", "est_qor"]

    start = time.time()
    allpops = []
    for rid in tqdm(range(iterations), f"NSGA search"):

        allpops.append(pd.DataFrame(parent).eval("generation=@rid"))

        offsprings = [mutate_conf(
            crossover_conf(random.choice(parent), random.choice(parent)),
            random.random() < mutation_rate
        ) for _ in range(q_size)]

        offsprings = evaluate_population(offsprings)
        population = parent + offsprings

        # selection of pareto frontiers
        next_parent = []
        while len(next_parent) < p_size:
            # select pareto frontier
            pareto = PyBspTreeArchive(len(metrics), minimizeObjective1=True, minimizeObjective2=False).filter(
                [[x[m] for m in metrics] for x in population], returnIds=True)

            current_pareto = [population[i] for i in pareto]
            missing = p_size - len(next_parent)

            if (len(current_pareto) <= missing):  # can we put all pareto frontier to the next parent
                next_parent += current_pareto
            else:  # distance crowding
                next_parent += crowding_reduce(current_pareto,
                                               missing, metrics)

            # delete nodes from the current population
            for i in reversed(sorted(pareto)):
                population.pop(i)

        parent = next_parent

    pd.concat(allpops, ignore_index=True).to_pickle(
        c.result_path(f"dump_nsga_{variant}.pkl.gz"))

    print("Run done ...")
    print()
    print("Done in %f seconds" % (time.time() - start))

    outc = {}
    for x in parent:
        while True:
            cid = f"nsga_{variant}_" + uuid1().hex[:8].upper()
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
    p.add_argument('--p_size', help='Parent population', type=int, default=200)
    p.add_argument('--q_size', help='Offspring population',
                   type=int, default=100)
    p.add_argument('--mutation_rate', help='Mutation rate',
                   type=float, default=0.1)

    args = p.parse_args()
    do_nsga(**vars(args))
# %%
