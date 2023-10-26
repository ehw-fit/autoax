import glob
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

    print(c.result_path(args.dataset + ".hw*.json.gz"))
    files_hw = glob.glob(c.result_path(args.dataset + ".hw*.json.gz"))
    files_qor = glob.glob(c.result_path(args.dataset + ".qor*.json.gz"))    

    print("# Readning files: \n", "\n".join(files_hw+files_qor))

    if not c.confirm_yes("Do you want to join the results?"):
        return
    
    for fn in files_hw + files_qor:
        print(f"# Reading {fn}")
        input_data = json.load(gzip.open(fn, "rt"))
        for d in input_data:
            data[d].update(input_data[d])
            index = data[d].keys()
    
    print("# features")
    for k in index:
        print(f" - {k}")
    

    o = c.block_on_result(args.dataset + ".eval.json.gz")
    json.dump(data, gzip.open(o, "wt"), indent=2)
if __name__ == "__main__":
    main()