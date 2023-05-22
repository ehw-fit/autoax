#%%%
import json
import gzip
import zipfile
import pandas as pd
from tqdm import tqdm
#%%

class VerilogGenerator:
    def __init__(self):
        self.df_lib = pd.read_pickle("components/data/circ.lib.pkl.gz").set_index("verilog_entity")
        self.zf_lib = zipfile.ZipFile("components/data/circ_lib.zip")

        self.templates = {
            i:open(f"templates/dct_circuit_c{i}.v").read() for i in [1, 2, 3, 4]
        }

        
    def generate_verilog(self, mcm=None, **kwargs):
        added = []
        lib_verilog = []
        for k, v in kwargs.items():
            if k == "uid": continue
            lib = self.df_lib.loc[v, "verilog"]
            if lib not in added:
                lib_verilog.append(self.zf_lib.open(lib).read().decode())
                added.append(lib)
            

        ver = self.templates[mcm]
        for k, v in kwargs.items():
            if f'"{k}"' not in ver:
                print(f"[Notice] {k} not in mcm {mcm}")
            ver = ver.replace(f'"{k}"', v)
        return "\n".join(lib_verilog + [ver])


    def create_verilog(self, configs, zip_filename):
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zf:
            for uid, c in tqdm(configs.items(), f"Writing {zip_filename}"):
                verilog = self.generate_verilog(**c, uid=uid)
                verf = zf.open(f"{uid}.v", "w")
                verf.write(verilog.encode())
                verf.close()

if __name__ == "__main__":
    VerilogGenerator().create_verilog(
        json.load(gzip.open("configs/accurate.json.gz")),
        "data/verilog_accurate.zip")
    # %%

    VerilogGenerator().create_verilog(
        json.load(gzip.open("configs/random.json.gz")),
        "data/verilog_random.zip")
    # %%
