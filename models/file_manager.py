# =============================================================================
# file_manager.py
#
# created  26 July 2017 Lungsi
# modified 29 August 2017 Lungsi
#
# This py-file contains file functions, initiated by
#
# from models import file_manager
#
# and individual file_manager initiated by:
#
# 1. file_manager.get_file_path ( dir_name=["model-predictions", "cells",
#                                           "PC2015Masoli"],
#                                 file_name="vm_soma" )
#    note: This utility is implemented by the                               
#
# 2. file_manager.get_model_lib_path ( model_scale="cells",
#                                      model_name="PC2015Masoli" )
#    note: This utility is implemented by the py-files (__init__)
#          containing models written in NEURON simulator. For example,
#          for PC2015Masoli at cellular ("cells") scale of model, the
#          above command is used. Regardless of whether the NEURON model
#          is compiled or not this command returns the mod-path (NEURON
#          model path to mod-files) and lib-path (compiled path) of the
#          model.
#
# 3. file_manager.check_and_make_directory ( "model-predictions",
#                                            "cells",
#                                            "PC2015Masoli" )
#    note: This utility is implemented by the py-files (capability method)
#          containing models written in NEURON simulator. The simulation
#          results of are saved in the desired location. The way it is used
#          here is /model-predictions/cells/PC2015Masoli
#          This returns the above directory path.
#
# 4. file_manager.get_build_path ( current_working_path,
#                                  directory_name )
#    note: This utility is implemented by check_and_make_directory().
#          Based on the string of the desired directory path this utility
#          creates the directory (if its not already created) and
#          subdirectories along the current_working_path. The end
#          subdirectory is where the simulation result is planned to save in.
#          This returns the built path.
#          NOTICE that get_build_path() is called in check_and_make_directory()
#
# =============================================================================

import os


def get_file_path(dir_names=["model-predictions", "cells"], file_name=None):
    """
    Use case: get_file_path(dir_names=["model-predictions", "cells",
                                       "PC2015Masoli"],
                            file_name="vm_soma.txt")
    Note: This is very similar to get_prediction_file()
          The implementation is different.
          arguments for get_prediction_file are
              1. model_name = "PC2015Masoli"
              2. file_name = vm_soma.txt
    """
    dir_path = os.getcwd()
    for dirs in dir_names:
        dir_path += os.sep + dirs
    dir_path = dir_path + os.sep # add a slash to indicate all are folders
    file_path = os.path.dirname(dir_path) + os.sep + file_name
    return file_path


def get_model_lib_path(model_scale=None, model_name=None):
    """
    Use case: get_model_lib_path(model_scale="cells", model_name="PC2015Masoli")
    where model_name is found by calling the get_available_models() function like
    get_available_models(model_scale="cells")
    """
    current_working_path = os.getcwd() + os.sep + "models"
    model_path = current_working_path + os.sep + model_scale + os.sep + model_name
    model_mod_path = model_path + os.sep + "mod_files"
    model_lib_path = os.path.dirname(model_mod_path) + os.sep + "x86_64" + \
                          os.sep + ".libs" + os.sep + "libnrnmech.so.0" 
    return model_mod_path, model_lib_path


def check_and_make_directory(*directory_names): #"model_predictions"
    """
    Use case: check_and_make_directory("model-predictions", "cells", "PC2015Masoli")
    where this function takes a variable number of directory names (string).
    ------------------------------------
    The directory names are given as variable number of arguments is such that:
    the first is checked/made in the root path,
    the second is checked/made along the path_w/_first_name,
    the third is checked/made along the path_w/_second_name
    and so on ...
    """
    root_path = os.getcwd() #+ os.sep + "models"
    current_working_path = root_path # initialize
    if len(directory_names) == 0: # raise error if no directory name is given
        raise ValueError("Must have at least one argument as a string for a directory name.")
    else:
        for dir_name in directory_names:
            # build the directory along the current_working_path
            built_path = get_build_path( current_working_path, dir_name )
            # check that the dir_name exists
            if not os.path.exists(dir_name): # if it does not exists
                os.makedirs(built_path)  # create the directory
            # set path to the current dir_name for checking the next dir_name
            os.chdir(built_path)
            # update the current current_working_path
            current_working_path = built_path
    os.chdir(root_path) # reset to root_path
    return built_path


def get_build_path(current_working_path, directory_name):
    """
    get_build_path_(current_working_path, directory_name)
    Use case-1:
    current_working_path = "/CerebellumModels"
    directory_name = "model-predictions"
    Use case-2:
    current_working_path = "/CerebellumModels/model-predictions"
    directory_name = "cells"
    Use case-3:
    current_working_path = "/CerebellumModels/model-predictions/cells"
    directory_name = "PC2015Masoli"
    And so on ...
    """
    return current_working_path + os.sep + directory_name


def get_prediction_file( model_name = "CellYearAuthor",
                         file_name = "something.txt" ):
    """
    Use case: get_prediction_file( model_name="PC2015Masoli",
                                   region_of_interest="vm_soma" )
    Note: This is very similar to get_file_path()
          The implementation is different.
          arguments for get_file_path are
              1. dir_names = list of string of directory names
              2. file_name = vm_soma.txt
    """
    cwd = os.getcwd() + os.sep + "model-predictions" + os.sep
    dir_path = [ os.path.join(root, name)
                 for root, dirs, files in os.walk(cwd)
                 for name in dirs
                 if name == model_name ]
    if not dir_path:
        print("There is no directory called " + model_name)
    else:
        file_path = [ os.path.join(root, name)
                      for root, dirs, files in os.walk(dir_path[0])
                      for name in files
                      if name == file_name ]
        if not file_path:
            print("There is no file name called " + file_name)
        else:
            return file_path[0]
#
#
