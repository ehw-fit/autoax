import gzip
import json
import uuid
import argparse
from autoax import Config
import os
import pandas as pd

def main():
    p = argparse.ArgumentParser()
    p.add_argument('config', help='Config file (yaml)')
    p.add_argument('dataset', help='Dataset file form results (e.g. random)')

    args = p.parse_args()

    c = Config(args.config)


    res_dir = os.path.join(c.cwd, "synth")
    os.path.exists(res_dir) or os.makedirs(res_dir)
    
    fn = c.result_path(args.dataset + ".json.gz")
    print(f"# Reading {fn}")
    data = json.load(gzip.open(fn))

    hw = json.load(gzip.open(c.result_path(args.dataset + ".hw.json.gz"), "rt"))
    qor = json.load(gzip.open(c.result_path(args.dataset + ".qor.json.gz"), "rt"))

    for d in data:
        data[d].update(hw[d])
        data[d].update(qor[d])
        index = data[d].keys()
    
    print("# features")
    for k in index:
        print(f" - {k}")
    

    o = c.block_on_result(args.dataset + ".eval.json.gz")
    json.dump(data, gzip.open(o, "wt"), indent=2)
if __name__ == "__main__":
    main()