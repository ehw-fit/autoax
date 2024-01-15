
# This script is used to generate the lib_tuples.cpp file
import gzip
import json
import argparse

from tqdm import tqdm
from autoax import Config
import os
import re

def check_design(f):
    lns = f.readlines()
    if lns[0].strip():
        print("problem")
    for l in lns:
        if "blackbox" in l:
            return False
    return True
def parse_power(f):
    d = f.readlines()
    f.close()

    # radek s total
    for x in d:
        if x[:5] == "Total":
            line = x[:-1] # bez \n

    pwr = re.split(r"\s+", line)[1:]
    assert pwr[-1] == "mW"
    return {"pdk45_pwr": float(pwr[-2])}

def parse_time(f):
    d = f.readlines()
    f.close()

    # radek s total
    for x in d:
        if "data arrival time" in  x:
            line = x[:-1] # bez \n

    return {"pdk45_delay": float(re.split(r"\s+", line)[-1])}


def parse_resource(f):
    d = f.readlines()

    # radek s total
    for x in d:
        if "Total" in  x:
            line = x[:-1] # bez \n

    return {"pdk45_area": float(re.split(r"\s+", line)[-1])}



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

    tmp_path = c.temporary_path(f"dc/{args.dataset}/synth")

    result = c.block_on_result(args.dataset + ".hw.dc.json.gz")

    res = {}
    all = True
    done = 0
    total = 0
    for i in tqdm(data):
        total += 1
        ex = os.path.exists(os.path.join(tmp_path, i, "power_opt.rep"))
        if not ex:
            print("missing", i)
            all = False
            continue
        done += 1
        d = {}

        with open(os.path.join(tmp_path, i, "cell_opt.rep")) as f:
            d = {**d, **parse_resource(f)}
        
        with open(os.path.join(tmp_path, i, "time_opt.rep")) as f:
            d = {**d, **parse_time(f)}

        with open(os.path.join(tmp_path, i, "power_opt.rep")) as f:
            d = {**d, **parse_power(f)}

        with open(os.path.join(tmp_path, i, "check.rep")) as f:
            if not check_design(f):
                all = False

        res[i] = d

    
    
    if not all:
        print("not all done ... done {} of {} ({:.2%})".format(done, total, float(done) / total))
        return
    
    json.dump(res, gzip.open(result, "wt"), indent=2)
    
if __name__ == "__main__":
    main()