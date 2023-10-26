[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![arXiv](https://img.shields.io/badge/arXiv-2303.04734-b31b1b.svg)](https://arxiv.org/abs/2303.04734)


# Xel-FPGAs
This repository presents a basic scheme for evaluating Xel-FPGAs algorithm for automatic approximation of hardware accelerators. 

_Generation and exploration of approximate circuits and accelerators has been a prominent research domain to achieve energy-efficiency and/or performance improvements. This research has predominantly focused on ASICs, while not achieving similar gains when deployed for FPGA-based accelerator systems, due to the inherent architectural differences between the two. In this work, we propose a novel framework, Xel-FPGAs, which leverages statistical or machine learning models to effectively explore the architecture-space of state-of-the-art ASIC-based approximate circuits to cater them for FPGA-based systems given a simple RTL description of the target application. We have also evaluated the scalability of our framework on a multi-stage application using a hierarchical search strategy. The Xel-FPGAs framework is capable of reducing the exploration time by up to 95%, when compared to the default synthesis, place, and route approaches, while identifying an improved set of Pareto-optimal designs for a given application, when compared to the state-of-the-art._

```bibtex
@INPROCEEDINGS{FITPUB13036,
   author = "S. Bharath Prabakaran and Vojtech Mrazek and Zdenek Vasicek and Lukas Sekanina and Muhammad Shafique",
   title = "Xel-FPGAs: An End-to-End Automated Exploration Framework for Approximate Accelerators in FPGA-Based Systems",
   pages = 9,
   booktitle = "Proceedings of the IEEE/ACM International Conference on Computer-Aided Design",
   year = 2023,
   language = "english",
}
```

## Requirements:
See [requirements.txt](requirements.txt) (you can modify the desired version, there is no strict limitation of the versions). 

It is also necessary to have installed [ABC](https://github.com/berkeley-abc/abc) in the system and to be available as `berkley-abc` command. If you have a different location, please modify [autoax/abcsynth.py](autoax/abcsynth.py) file or make an alias. At debian-based linux you can install it by a command

```bash
sudo apt install berkley-abc
```

## Example application
The system is easily configurable. You can follow an example for the Sobel edge detector listed in a folder [sobel](sobel/). An input is a fully described library of approximate components, configuration of experiments and hardware and software models.

The configuration can specify multiple variants of features used. The proposed model is fully extensible for introducing new operators etc. The example analysis can be seen in [sobel/analysis.ipynb](sobel/analysis.ipynb).

## Library description
Approximate library needs to have specified some parameters (hardware and error parameters) and links to particular C functions and Verilog files.
```json
{
    "pdk45_pdp":0.00925618,
    "cfun":"add_8_0u_8_0u_9u_norm8_a_2_000000_run_00008",
    "pdk45_pwr":0.021526,
    "verilog":"add_8_0u_8_0u_9u_norm8_a_2_000000_run_00008.v",
    "verilog_entity":"add_8_0u_8_0u_9u_norm8_a_2_000000_run_00008",
    "bw":8,
    "pdk45_delay":0.43,
    "pdk45_area":45.991402
}
```

## AutoAx run
If you want to run AutoAx for Xel-FPGAs, please follow this pipeline. Note that evaluation to get exact values needs to have Vivado and C++ installed,

```bash
python 01_generate_initial.py --count 1000 sobel/config.yml 
```
Then run QoR and Vivado evaluation (see next lines). 

```bash
# finally, join the results

python join_results.py sobel/config.yml random

# for all variants run the training (this is for variant v2; tg)
python 02_learn.py sobel/config.yml v2

# you can plot or evaluate the results, see sobel/analyze.ipynb notebook

# Run the Hill-climber search for variant v2
python 03_search_hc.py sobel/config.yml v2 --population=10 --iterations=1000
cls=hc_v2
# run evaluation of hc_v2 instead of random; ie replace the class random to hc_v2

python join_results.py sobel/config.yml $cls




# Same can be done for NSGA-II algorithm
python 03_search_nsga.py sobel/config.yml v2 --p_size=200 --q_size=100 --iterations=100
cls="nsga_v2"
```


## Evaluation
All runs needs to be evaluated for Quality (software simulation) and for Hardware parameters. In general, it assigns c++ functions or verilog modules to some template. Then the evaluation or synthesis is run and finally the particular columns cames to the final dataset.

### QoR evaluation
```bash
cls=random
python evaluate_qor.py sobel/config.yml $cls

cd sobel/eval
mkdir build
cd build
cmake ..
make
# run the evaluation for selected configurations
./axsobel ../../../img/* < ../../res/$cls.runlist  | tee ../../res/$cls.qor
cd ../../..

python parse_qor.py sobel/config.yml $cls sobel/res/$cls.qor
```

### Vivado evaluation
```bash
cls=random
python evaluate_hw.py sobel/config.yml $cls
# repeat this part to run in parallel
shuf sobel/res/$cls.synth.tcl > sobel/res/$cls.synth2.tcl
vivado  << EOF
source vivado.tcl
source sobel/res/$cls.synth2.tcl
exit
EOF

python status_vivado.py sobel/config.yml $cls
python parse_vivado.py sobel/config.yml $cls
```


### DCshell evaluation
We support also evaluation by Synopsys Design Compiler. It creates features pdk45_pwr, pdk45_area, pdk45_delay.

```bash
 python evaluate_hw.py --mode dc sobel/config.yml random
dc_shell << EOF
pdk45 # load the techlibrary (not implemented here, use own!)
source dcshell.tcl # function to synthesize
source sobel/res/random.synth.tcl # synth all
EOF
python parse_dc.py sobel/config.yml $cls
```

## Own ML model
If you want to use own ML model, you can add a static function
    Config.model_loopback(name) -> model (see 02_learn.py)

```py
def ownLoopback(m):
    if m == "my_model":
        from sklearn.ensemble import RandomForestRegressor
        return RandomForestRegressor(n_estimators=1000)
    assert False

from autoax import Config
Config.model_loopback = ownLoopback
```
    
## Own feature extractor
You can use another features - see sobel/abcfeatures.py as an example.
