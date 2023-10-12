# %%
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from autoax import Config, FeatureExtractor, ABClib, ABCall
import argparse
import json
import gzip
import joblib




if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument('config', help='Config file (yaml)')
    p.add_argument('variant', help='Variant (from config file)')

    args = p.parse_args()

    c = Config(args.config)

    variant = c.get_variant(args.variant)
    
    elements = json.load(gzip.open(c.result_path("random.eval.json.gz"), "rt"))
    libraries = c.components()

    items = c.components_keys()
    print("## Evaluating variant ", args.variant)

    quality = []
    for obj in ["hw", "qor"]:
        print("### Objective ", obj)

        # load configuration
        ft = variant["features"]
        features = ft[obj] if obj in ft else []
        features_glob = ft[obj + "glob"] if obj + "glob" in ft else []
        objective = variant["objectives"][obj]

        assert(len(features) + len(features_glob) > 0)

        # Prepare features
        fe = FeatureExtractor(c, modules=variant["modules"])
        fe.setFeatures(features)
        fe.setFeaturesGlobal(features_glob)

        ds = {}
        y = {}
        for k, l in tqdm(elements.items(), total=len(elements), desc="Extracting features"):
            ds[k] = fe(l)
            y[k] = l[objective]

        X = pd.DataFrame(ds).T
        y = pd.Series(y)



        # Create data
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.30, random_state=1234)
        
        # Output dump
        X_res = X.copy()
        X_res[f"{obj}_train"] = False
        X_res.loc[X_train.index, f"{obj}_train"] = True
        X_res[f"{obj}_desired"] = y

        # Prepare path for storing
        os.path.exists(c.result_path(f"models_{args.variant}")) or os.makedirs(c.result_path(f"models_{args.variant}"))
        
        for mname, model in variant["ml"].items():
            model.fit(X_train, y_train)
            print("### training", mname, obj, model.score(X_test, y_test))
            joblib.dump(model, c.block_on_result(f"models_{args.variant}/{obj}.{mname}.joblib"))

            X_res[f"{obj}_{mname}"] = model.predict(X)
            quality.append({
                "model": mname,
                "objective": obj,
                "test_score": model.score(X_test, y_test),
                "train_score": model.score(X_train, y_train)
            })


        X_res.to_pickle(c.block_on_result(f"models_{args.variant}/learn.{obj}.pkl.gz"))

    df_quality = pd.DataFrame(quality)
    df_quality.to_pickle(c.block_on_result(f"models_{args.variant}/quality.pkl.gz"))
    print(df_quality)
