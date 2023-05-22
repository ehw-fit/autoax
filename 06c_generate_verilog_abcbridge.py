#%%%
import json
import gzip
import zipfile
import pandas as pd

VerilogGenerator = __import__("02_generate_verilog").VerilogGenerator
#%%

for mcm in [1, 2, 3, 4]:
    config = json.load(gzip.open(f"configs/bridge-abc-hc_mcm{mcm}_1000.json.gz"))
    
    VerilogGenerator().create_verilog(
        {x.replace("-", "_"): y for x, y in config.items()},
        f"data/verilog_bridge_abc_hc_mcm{mcm}_1000.zip")

    #df_nsgacontinue
    config = json.load(gzip.open(f"configs/bridge-abc-nsga_mcm{mcm}_1000x200.json.gz"))

    VerilogGenerator().create_verilog(
        {x.replace("-", "_"): y for x, y in config.items()},
        f"data/verilog_bridge_abc_nsga_mcm{mcm}_1000x200.zip")
# %%