

# This script is used to generate the lib_tuples.cpp file
import gzip
import json
import uuid
import argparse
from autoax import Config
import os


def main():
    p = argparse.ArgumentParser()
    p.add_argument('config', help='Config file (yaml)')
    p.add_argument('dataset', help='Dataset file form results (e.g. random)')
    p.add_argument('results', help='Result file')

    args = p.parse_args()

    c = Config(args.config)
    fn = c.result_path(args.dataset + ".json.gz")


    run_list = c.block_on_result(args.dataset + ".qor.json.gz")

    print(f"# Reading {fn}")
    data = json.load(gzip.open(fn))


    res = {}
    with open(args.results) as f:
        for line in f:
            row = line.split(";")

            if len(row) < 2: 
                continue

            if row[0] not in data:
                print("skipping", row[0])
                continue
            
            r = {}
            for l in row[1:]:
                l = l.strip()
                if not l:
                    continue
                k, v = l.split("=")
                r[k] = v

            res[row[0]] = r

    for d in data:
        if d not in res:
            print("!!! missing evaluation of config", d)
    


    print("# Creating " , run_list )

    
    json.dump(res, gzip.open(run_list, "wt"), indent=2)


if __name__ == "__main__":
    main()
