"""
Goal: synthesize all circuit by ABC to get #LUTs and delay
Output: circ.abc.pkl.gz
"""

import pandas as pd
import subprocess
import re
from tqdm import tqdm
import gzip
import os
import json

VerilogGenerator = __import__("02_generate_verilog").VerilogGenerator

class ABCsynth:
    def __init__(self):
        self.verilog_generator = VerilogGenerator()

    def runSynth(self, conf):
        verilog = self.verilog_generator.generate_verilog(uid="tmp_abc", **conf)

        #print(verilog)
        fname = "tmp/tmp_abc{}.v".format(os.getpid())
        open(fname, "w").write(verilog)
        #r = subprocess.run(["berkeley-abc", "-c", "read_verilog tmp.v; sweep; resyn2; ps -p"], stdout=subprocess.PIPE)
        r = subprocess.run(["berkeley-abc", "-c", f"read_verilog {fname}; if -K 6; ps -p"], stdout=subprocess.PIPE)

        res = r.stdout.decode("utf-8").split("\n")[-2]
        
        m = re.match(r"""
            (\W*\d+;\d+)?    # unprintable character
            ([^ ]+).*:.*     # name
            i\/o\s*=\s*(\d+)\/\s*(\d+) # i/o
            \s*lat\s*=\s*(\d+)   # lat
            \s*and\s*=\s*(\d+)   # and
            \s*lev\s*=\s*(\d+)   # lev
            \s*power\s*=\s*(\d+\.?\d*)   # power
            """, res, re.X) #/   14  lat =    0  and =     20  lev =  6  power =  24.26
        if m:
            _, g_name, g_in, g_out, g_lat, g_and, g_lev, g_power = m.groups()


            return {
                "abc_name": g_name,
                "abc_in" : int(g_in),
                "abc_out" : int(g_out),
                "abc_lat" : int(g_lat),
                "abc_and" : int(g_and),
                "abc_lev" : int(g_lev),
                "abc_power" : float(g_power),

            }

        m = re.match(r"""
            (\W*\d+;\d+)?    # unprintable character
            ([^ ]+).*:.*     # name
            i\/o\s*=\s*(\d+)\/\s*(\d+) # i/o
            \s*lat\s*=\s*(\d+)   # lat
            \s*nd\s*=\s*(\d+)    # nd
            \s*edge\s*=\s*(\d+)    # nd
            \s*aig\s*=\s*(\d+)    # nd
            \s*lev\s*=\s*(\d+)   # lev
            \s*power\s*=\s*(\d+\.?\d*)   # power
            """, res, re.X) #/   14  lat =    0  and =     20  lev =  6  power =  24.26
        assert m
        if m:
            _, g_name, g_in, g_out, g_lat, g_nd, g_edge, g_aig, g_lev, g_power = m.groups()


            return {
                "abc_name": g_name,
                "abc_in" : int(g_in),
                "abc_out" : int(g_out),
                "abc_lat" : int(g_lat),
                "abc_nd" : int(g_nd),
                "abc_edge" : int(g_edge),
                "abc_aig" : int(g_aig),
                "abc_lev" : int(g_lev),
                "abc_power" : float(g_power),

            }



if __name__ == "__main__":
    configs = json.load(gzip.open("configs/random.json.gz"))
    abc = ABCsynth()

    alld = []
    from time import time

    start = time()
    for uid, conf in tqdm(list(configs.items())):
        r = {"index": uid, **abc.runSynth(conf)}

        alld.append(r)

        break

    print("done in {0} s".format(time() - start))
    df_abc = pd.DataFrame(alld)
    print(df_abc)
    df_abc.to_pickle("data/random.abc.pkl.gz")