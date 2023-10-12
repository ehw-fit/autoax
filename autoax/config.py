from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .library import Library
from .abcfeatures import ABCall, ABClib
import os

class Config:
    """
    Configuration of one run od autoAx. Specifies the library
    and the components to use. The experiment also specifies
    the features to use for the ML estimator.

    If you want to use own ML model, you can add a function
    Config.model_loopback(name) -> model (see 02_learn.py)


    """

    model_loopback = None

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = load(open(config_file), Loader=Loader)
        self.cwd = os.path.dirname(config_file)
        self.libraries = {}

        self.model_loopback = None

        self._v_template = None

    

    def result_path(self, filename):
        """
        Creates a result path relative to the config file and 'results' configuration
        directory. If the directory doesn't exist, it is created.
        """
        p = os.path.join(self.cwd, self.config['results'], filename)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p
    
    

    def temporary_path(self, filename):
        """
        Creates a temporary path relative to the config file and 'temporary' configuration
        directory. If the directory doesn't exist, it is created.
        """
        p = os.path.join(self.cwd, self.config['temporary'], filename)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    def block_on_result(self, filename, relative = True):
        """
        Checks if the file exists and if it does, raises an error. This function
        helps to avoid overwriting results.
        """
        if relative:
            p = self.result_path(filename)
        else:
            p = filename
        if os.path.exists(p):
            # Explicitly prompt user if he wants to overwrite the file
            r = input("Result file {} already exists. Do you want to overwrite it? [y/N]".format(p))
            if r.lower() != "y":
                raise Exception("Result file {} already exists. If you want to rewrite it, delete it first".format(p))

        return p
    
    def components(self) -> dict:
        r = {}
        for c, lib in self.config['components'].items():
            if not lib in self.libraries:
                self.libraries[lib] = Library(lib, self, self.config["library"][lib])
            r[c] = self.libraries[lib]

        return r
    
    def components_keys(self):
        return sorted(self.config['components'].keys())
    

    def v_template(self):
        if not self._v_template:
            self._v_template = open(os.path.join(self.cwd, self.config["evaluate_verilog"])).read()
        return self._v_template
    
    
    def extract_verilog(self, uid, individual):
        template = self.v_template()
        vt = template
        vt = vt.replace("\"uid\"", uid)

        parsed = []

        for k, lib in self.components().items():
            comp = lib[individual[k]]
            l, f, ver = lib.extract_verilog(individual[k])
            if f not in parsed:
                parsed.append(f)
                vt += "\n\n" + ver.decode()

            template = template.replace("\"" + k + "\"", comp["verilog_entity"])

            vt = vt.replace("\"" + k + "\"", comp["verilog_entity"])

        return vt

    def get_variant(self, v):
        try:
            variant = self.config["variants"][v]
            m = []
            # if modules is string transform it to list
            if "modules" not in variant:
                variant["modules"] = []

            if isinstance(variant["modules"], str):
                variant["modules"] = [variant["modules"]]

            for k in variant["modules"]:
                # modules parsing
                if k == "ABClib":
                    m.append(ABClib(self))
                elif k == "ABCall":
                    m.append(ABCall(self))
                else:
                    raise ValueError("Unknown module: " + k)
            variant["modules"] = m


            models = {}
            for k in variant["ml"]:
                if k == "RandomForrest":
                    from sklearn.ensemble import RandomForestRegressor
                    models[k] = RandomForestRegressor()
                elif k == "SVC":
                    from sklearn.svm import SVR
                    models[k] = SVR()
                elif k == "BayesianRidge":
                    from sklearn.linear_model import BayesianRidge
                    models[k] = BayesianRidge()
                elif self.__class__.model_loopback:
                    models[k] = self.__class__.model_loopback(k)
                else:
                    raise ValueError("Unknown model: " + k)
            variant["ml"] = models


            return variant
        except KeyError:
            raise ValueError("Unknown variant in config: " + v + ". Known variants: " + str(self.config["variants"].keys()))