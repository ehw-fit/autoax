
# This script is used to generate the lib_tuples.cpp file
import gzip
import json
import uuid
import argparse
from autoax import Config
import os
import tqdm


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

    tmp_path = c.temporary_path(f"vivado/{args.dataset}/synth")

    tot = 0
    valid = 0
    for i in data:
        ex = os.path.exists(os.path.join(tmp_path, i, "results_resource.txt"))
        if ex:
            valid += 1
        tot += 1
    
    print(f"Valid: {valid}/{tot}")

if __name__ == "__main__":
    main()