import json
import gzip
import os
import zipfile


class Library:
    """
    Library of possible approximate components
    """

    def __init__(self, libname, config, params):
        self.config = config
        self.libname = libname
        self.params = params
        self.data = json.load(
            gzip.open(os.path.join(config.cwd, params['json']), 'rt'))
        self.verilog_zip = None

    def possible(self):
        """
        List of all possible IDs that can be obtainded from the library
        """
        return list(self.data.keys())

    def __getitem__(self, key):
        """
        Get the data for a specific ID
        """
        return self.data[key]

    def __str__(self):
        """
        String representation of the library
        """
        return self.libname + "[" + os.path.join(self.config.cwd, self.params['json']) + "]"

    def extract_verilog(self, key):
        """
        Extract the verilog for a specific ID
        returns library name, file name, and file content
        """
        if not self.verilog_zip:
            self.verilog_zip = zipfile.ZipFile(os.path.join(self.config.cwd, self.params["verilog"]))

        verilogfile = self.data[key]['verilog']
        return self.libname, verilogfile, self.verilog_zip.open(verilogfile).read()
