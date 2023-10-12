
# This script is used to generate the lib_tuples.cpp file
import gzip
import json
import argparse
from autoax import Config
import os
import re

def parse_power(data):
    in_sec11 = False
    units_watts = False
    ret = {}
    ret["power_dynamic"] = 0 # default
    for l in data:
        if l.startswith("1.1"):
            in_sec11 = True
        
        if l.startswith("1.2"):
            in_sec11 = False


        if in_sec11:
            if "Power (W)" in l:
                units_watts = True

            g = re.match(r"\| Slice Logic\s+\|\s*(\d+\.?\d*)\s*\|", l)
            if g:           
                ret["power_dynamic"] = float(g.group(1))

            g = re.match(r"\| Static Power\s+\|\s*(\d+\.?\d*)\s*\|", l)
            if g:           
                ret["power_static"] = float(g.group(1))

    if "power_dynamic" not in ret:
        print("".join([x.decode() for x in data]))

    assert units_watts # test if Power (W) is in the header
    assert "power_dynamic" in ret
    assert "power_static" in ret
    ret["power"] = ret["power_static"] + ret["power_dynamic"]
    return ret

def parse_resource(data):
    in_sec2 = False

    ret = {}
    for l in data:
        if l.startswith("2. "): in_sec2 = True
        if l.startswith("3. "): in_sec2 = False

        if not in_sec2: continue

        g = re.match(r"\| Slice\s+\|\s*(\d+)\s*\|", l)
        if g:           
            ret["slice"] = int(g.group(1))

        g = re.match(r"\| LUT as Logic\s+\|\s*(\d+)\s*\|", l)
        if g:           
            ret["lut"] = int(g.group(1))

    assert "slice" in ret
    assert "lut" in ret
    return ret


def parse_time(data):
    in_sec2 = False

    ret = {}
    for l in data:
        if l.startswith("1. "): 
            
            in_sec2 = True
            if l == "1. Logic Level Distribution\n":
                # zero delay model - only constant output! 
                ret["delay"] = 0
                ret["delay_net"] = 0
                ret["delay_logic"] = 0
                print(" --- ZERO DELAY")
        if l.startswith("2. "): in_sec2 = False

        if not in_sec2: continue

        #print(l, end="")

        g = re.match(r"\| Path Delay\s+\|\s*(\d+\.?\d*)\s*\|", l)
        if g:           
            ret["delay"] = float(g.group(1))

        g = re.match(r"\| Logic Delay\s+\|\s*(\d+\.?\d+)\(.*", l)
        if g:           
            ret["delay_logic"] = float(g.group(1))

        g = re.match(r"\| Net Delay\s+\|\s*(\d+\.?\d+)\(.*", l)
        if g:           
            ret["delay_net"] = float(g.group(1))

    #assert "delay" in ret
    #assert "delay_logic" in ret
    #assert "delay_net" in ret
    return ret



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

    result = c.block_on_result(args.dataset + ".hw.json.gz")

    res = {}
    all = True
    for i in data:
        ex = os.path.exists(os.path.join(tmp_path, i, "results_resource.txt"))
        if not ex:
            print("missing", i)
            all = False
            continue

        d = {}

        with open(os.path.join(tmp_path, i, "results_resource.txt")) as f:
            d = {**d, **parse_resource(f)}
        
        with open(os.path.join(tmp_path, i, "results_time.txt")) as f:
            d = {**d, **parse_time(f)}

        with open(os.path.join(tmp_path, i, "results_power.txt")) as f:
            d = {**d, **parse_power(f)}
        res[i] = d

    
    
    if not all:
        print("not all done")
        return
    
    json.dump(res, gzip.open(result, "wt"), indent=2)
    
if __name__ == "__main__":
    main()