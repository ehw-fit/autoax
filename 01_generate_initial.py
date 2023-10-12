from autoax import Config
import argparse
import numpy as np
import uuid
import json, gzip

def generate_initial(config : Config, count : int, seed = None):

    res_path = config.block_on_result("random.json.gz")
    if seed:
        np.random.seed(seed)

    print("Possible assignments: ")
    possible = 1
    for k, library in config.components().items():
        p = len(library.possible())
        print(f" - {k} (lib: {library}) - {p}")
        possible *= p
    print("=== Total possible: ", possible)
    

    
    configs = {}
    for i in np.arange(count):
        uid = "random_" + str(uuid.uuid4().hex[:6].upper())
        r = {}
        for k, library in config.components().items():
            r[k] = np.random.choice(library.possible())
        
        configs[uid] = r


    json.dump(configs, gzip.open(res_path, "wt"), indent=4)
    print("Generated ", len(configs), " random configurations to ", res_path)
    


def main():
    p = argparse.ArgumentParser()
    p.add_argument('config', help='Config file (yaml)')
    p.add_argument('--count', help='Number of random confiurations to generate', default=5000, type=int)

    args = p.parse_args()

    c = Config(args.config)

    generate_initial(c, args.count)

if __name__ == '__main__':
    main()


