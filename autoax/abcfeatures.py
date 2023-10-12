from .abcsynth import ABCsynth
import gzip
import json
import os
from typing import Dict, Any
from .library import Library

class ABClib:
    def __init__(self, config):
        self.config = config
        self.abc = ABCsynth()
        try:
            self.cache = json.load(
                gzip.open(config.temporary_path("abclib.cache.json.gz"), "rt"))
        except:
            self.cache = {}

    def register_features(self):
        return {f"abclib_{k}": self.return_features(f"abc_{k}")
                for k in ["lat", "and", "lev", "power"]
                }

    def _fill_cache(self, lib: Library, i: str):
        if i not in self.cache:
            # print(lib.extract_verilog(i)[2].decode())
            self.cache[i] = self.abc.runSynth(
                lib.extract_verilog(i)[2].decode(),
                fname=self.config.temporary_path(
                    "abc_lib_{}.v".format(os.getpid())),
                raise_on_error=True
            )
            json.dump(self.cache, gzip.open(self.config.temporary_path(
                "abclib.cache.json.gz"), "wt"), indent=4)

        return self.cache[i]

    def return_features(self, key):
        def f(lib: Library, i: str):
            return self._fill_cache(lib, i)[key]
        return f


class ABCall:
    def __init__(self, config):
        self.config = config
        self.abc = ABCsynth()
        self.ckeys = config.components_keys()
        try:
            self.cache = json.load(
                gzip.open(config.temporary_path("abcall.cache.json.gz"), "rt"))
        except:
            self.cache = {}

    def register_features(self):
        return {f"abcall_{k}": self.return_features(f"abc_{k}")
                for k in ["lat", "and", "lev", "power"]
                }

    def _fill_cache(self, individual: Dict[str, Any]):
        i = ";".join([f"{k}={individual[k]}" for k in self.ckeys])
        if i not in self.cache:
            # print(lib.extract_verilog(i)[2].decode())
            self.cache[i] = self.abc.runSynth(
                self.config.extract_verilog("abc_ent", individual=individual),
                fname=self.config.temporary_path(
                    "abc_glob_{}.v".format(os.getpid())),
                raise_on_error=True
            )
            json.dump(self.cache, gzip.open(self.config.temporary_path(
                "abcall.cache.json.gz"), "wt"), indent=4)

        return self.cache[i]

    def return_features(self, key):
        def f(individual: Dict[str, Any]):
            return self._fill_cache(individual)[key]
        return f
