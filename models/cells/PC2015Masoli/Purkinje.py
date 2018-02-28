import os

from Purkinje_original import PurkinjeTemplate

class Purkinje(object):
    def __init__(self):
        self.cwd = os.getcwd()
        self.path_to_files = self.cwd + os.sep + "models" + os.sep + \
                             "cells" + os.sep + "PC2015Masoli" + os.sep

    def construct_pc(self):
        os.chdir(self.path_to_files)
        self.cell = PurkinjeTemplate()
        os.chdir(self.cwd)

    def destroy_pc(self):
        del self.cell
