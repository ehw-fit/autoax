#%%%
import json
import gzip
import zipfile
import pandas as pd

VerilogGenerator = __import__("02_generate_verilog").VerilogGenerator
#%%

for mcm in [1, 2, 3, 4]:

    VerilogGenerator().create_verilog(
        json.load(gzip.open(f"configs/nsga_mcm{mcm}_10000x200.json.gz")),
        f"data/verilog_nsga_mcm{mcm}_10000x200.zip")
# %%