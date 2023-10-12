

from typing import Any, Dict
from .config import Config

class FeatureExtractor:
    def __init__(self, config: Config, modules=[]):
        self.features_functions = {}
        self.features = []
        self.features_global = []
        
        self.config = config
        self.components_keys = config.components_keys()
        self.libraries = config.components()

        for m in modules:
            self.addModule(m)


    def setFeatures(self, features):
        self.features = features

    def setFeaturesGlobal(self, features):
        self.features_global = features

    def addModule(self, module):
        self.features_functions.update(module.register_features())

    def __call__(self, individual: Dict[str, Any]):
        r = {}
        for component in self.components_keys:
            lib = self.libraries[component]
            i = lib[individual[component]]
            for feature in self.features:
                # if feature is callable
                if feature in self.features_functions:
                    r[component + "_" +
                        feature] = self.features_functions[feature](lib, individual[component])
                else:
                    try:
                        r[component + "_" + feature] = i[feature]
                    except KeyError:
                        raise KeyError(
                            "Feature {} not found in component {}[{}]. Possible features: {}".format(feature, component, individual[component], ",".join(i.keys())))

        for feature in self.features_global:
            if feature in self.features_functions:
                r[feature] = self.features_functions[feature](individual)
            else:
                r[feature] = individual[feature]

        return r
