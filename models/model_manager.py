# =============================================================================
# model_manager.py
#
# created  26 July 2017 Lungsi
# modified 29 August 2017 Lungsi
#
# This py-file contains functions to manage models, initiated by
#
# from models import model_manager
#
# and individual file_manager initiated by:
#
# 1. model_manager.get_available_models ( model_scale="cells" )
#
#    note: If you want to get the list of available models for a particular
#          scale of modelling (say, "cells") use the above command.
#
# 2. model_manager.check_and_compile_model ( model_mod_path,
#                                            model_lib_path )
#    note: This utility is implemented by the py-files (__init__)
#          containing models written in NEURON simulator.
#          a. from models imprt file_manager
#          b. model_mod_path, model_lib_path =
#             file_manager.get_model_lib_path( model_scale="cells",
#                                              model_name="PC2015Masoli" )
#          Based on the model_mod_path and model_lib_path this function
#          checks if the model is already compiled in the lib-path.
#          If its not compiled the model mod-files in the mod-path
#          is compiled.
#          c. 2.
#
# =============================================================================

import os
import subprocess

from neuron import h


def get_available_models(model_scale=None):
    """
    Use case: get_available_models(model_scale="cells")
    ------------------------------------
    Function gives you the list of available models for the chosen
    modelling scale.
    """
    root_path = os.getcwd()
    model_path = root_path + os.sep + "model" + os.sep + model_scale
    os.chdir(model_path) # change pwd path to model_path
    model_directories = \
            [item for item in os.listdir(os.getcwd()) if os.path.isdir(item)]
    #print os.path.isdir(model_directories[0]) # will return True
    os.chdir(os.path.dirname(root_path)) # reset to original path
    #print os.path.isdir(model_directories[0]) # will return False
    return model_directories #return os.listdir(model_path)


def check_and_compile_model(model_mod_path, model_lib_path):
    """
    Use case: check_and_compile_model(model_mod_path, model_lib_path)
    where model_mod_path and model_lib_path strings are obtained by calling the
    get_model_lib_path() function like
    get_model_lib_path(model_scale="cells", model_name="PC2015Masoli")
    ------------------------------------
    If compiled NEURON files are not already present the mod files
    are compiled. The mod directory & compiled directory are both
    childs of their parent model directory.
    """
    if os.path.isfile(model_lib_path) is False:
        #os.system("cd " + modelpath + "; nrnivmodl")
        #os.system("nrnivmodl " + modelpath)
        paths = os.path.split(model_mod_path)
        subprocess.call("cd " + paths[0] + ";nrnivmodl " + paths[1], shell=True)
    else:  # uncomment to debug this function
        print("compiled files already exists")
#
#
