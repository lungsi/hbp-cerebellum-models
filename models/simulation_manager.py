# =============================================================================
# simulation_manager.py
#
# created  26 July 2017 Lungsi
#
# This py-file contains file functions, initiated by
#
# from models import simulation_manager
#
# and individual file_manager initiated by:
#
# 1. simulation_manager.discover_cores_activate_multisplit(h)
#
#    note: This utility is implemented by the py-files (__init__)
#          containing models written in NEURON simulator.
#
# 2. simulation_manager.initialize_and_run_NEURON_model(h)
#
#    note: This utility is implemented by the py-files (capability method)
#          containing models written in NEURON simulator.
#
# 3. simulation_manager.check_capability_availability( capability_name =
#                                                      "produce_spike_train",
#                                                      CerebUnitCapability =
#                                                         ProducesSpikeTrain )
#    note: This utility is implemented by the py-files (capability method)
#          containing models written in NEURON simulator. It checks if the
#          current capability is available in the cerebunit module. If not
#          it returns an AttributeError.
#
# 4. simulation_manager.save_predictions ( model,
#                                          prediction_dir_path )
#    note: This utility is implemented by the py-files (capability method)
#          containing models written in NEURON simulator. For an instantiated
#          model (template) the simulation result is saved in txt-file/s
#          whose filename is given by "vm_soma", "vm_NOR3", etc ... These
#          txt-file/s will be saved in the desired path.
#
# =============================================================================

import os
import subprocess
import multiprocessing  # for utilities.discover_cores_activate_multisplit(h)
import time
import sys        # for clone_method()
import types      # for clone_method
import functools  # for clone_method

from neuron import h
import numpy as np


def discover_cores_activate_multisplit(h):
    """
    Use case: discover_cores_activate_multisplit(h)
    where h is a module; from neuron import h.
    """
    # discover no. of cores in 1CPU and activate multisplit to use all cores
    cores = multiprocessing.cpu_count()
    h.load_file("parcom.hoc")
    p = h.ParallelComputeTool()
    p.change_nthread(cores, 1)
    p.multisplit(1)
    #print "cores", cores


# ++++++++++++++++++++++set_runtime_parameters+++++++++++++++++++++
# created:  03 August 2017
# modified: 01 January 2018 (renamed from set_simulation_properties)
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def set_runtime_parameters( model, setup_parameters ):
        model.h.dt = setup_parameters["dt"]
        model.h.celsius = setup_parameters["celsius"]
        model.h.tstop = setup_parameters["tstop"]
        model.h.v_init = setup_parameters["v_init"]


# +++++++++++++++++++++set_stimulation_properties++++++++++++++++++++
# created:  01 September 2017
# modified: 10 October 2017
# Note: This function is NOT model capability function.
#       This function takes four arguments:
#       time_step = 
#       temp =
#       t_final =
#       v_init =
#       ****IMPORTANT*****
#       With NEURON stimulus setup as a seperate python function it
#       requires that the returned stimulus is RE-set to the cell.soma
#       This is why the function returns the list of stimuli
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def set_stimulation_properties( model, current_parameters ):
    model.list_of_stimuli = []
    n = len(current_parameters) # number of currents
    # =============first create 'n' IClamps
    for i in range(n):
        # IClamp for each stimulus
        model.list_of_stimuli.append( model.h.IClamp(0.5, sec=model.cell.soma) )
        model.list_of_stimuli[i].amp = \
                    current_parameters["current"+str(i+1)]["amp"]
        model.list_of_stimuli[i].dur = \
                    current_parameters["current"+str(i+1)]["dur"]
        model.list_of_stimuli[i].delay = \
                    current_parameters["current"+str(i+1)]["delay"]
    return model.list_of_stimuli

def inject_current( model, current_parameters, stim_type="IClamp" ):
    model.list_of_stimuli = []
    n = len(current_parameters) # number of currents
    # =============first create 'n' IClamps
    for i in range(n):
        key = "current"+str(i+1)
        if stim_type=="IClamp":
            # IClamp for each stimulus
            model.list_of_stimuli.append( model.h.IClamp(0.5, sec=model.cell.soma) )
            model.list_of_stimuli[i].amp = \
                    current_parameters["current"+str(i+1)]["amp"]
            model.list_of_stimuli[i].dur = \
                    current_parameters["current"+str(i+1)]["dur"]
            model.list_of_stimuli[i].delay = \
                    current_parameters["current"+str(i+1)]["delay"]
        elif stim_type=="IRamp":
            model.list_of_stimuli.append( model.h.IRamp(0.5, sec=model.cell.soma) )
            model.list_of_stimuli[i].delay = \
                    current_parameters[key]["delay"]
            model.list_of_stimuli[i].dur = \
                    current_parameters[key]["dur"]
            model.list_of_stimuli[i].amp_initial = \
                    current_parameters[key]["amp_initial"]
            if i==0:
                model.list_of_simuli[i].amp_final = \
                        current_parameters[key]["amp_final"]
            else:
                model.list_of_stimuli[i].amp_final = \
                        current_parameters[key]["amp_final"] \
                        - current_parameters[key]["amp_initial"]
    return model.list_of_stimuli
    
def initialize_and_run_NEURON_model(model):
    """
    Use case: initialize_and_run_NEURON_model(h)
    where h is a module; from neuron import h.
    """
    model.h.finitialize()
    start_time = time.clock()
    model.h.run()
    print ("--- %s seconds ---" % (time.clock() - start_time))


def check_capability_availability(capability_name="None",
                                  CerebUnitCapability="None"):
    """
    Use case:
    check_capability_availability( capability_name = "produce_spike_train",
    CerebUnitCapability = ProducesSpikeTrain )
    where "produce_spike_train" is the name of the/a method in the model class;
    for eg, the class PurkinjeCell with the method produce_spike_train.
    ProducesSpikeTrain is an imported class; for eg,
    from cerebellum_cell_capability import ProducesSpikeTrain.
    """
    # check that the chosen capability is an available attribute
    if not capability_name in dir(CerebUnitCapability):
        raise AttributeError(CerebUnitCapability.__name__ + " has no method " + capability_name)
    else:
        print(CerebUnitCapability.__name__ + " has the method " + capability_name)


# created  18 August 2016 Lungsi
# modified 22 September 2017 Lungsi
def save_predictions(model, response_type, dir_path):
    """
    Use case: save_predictions(model, response_type, model.prediction_dir_pat)
    where model = self and therefore
          model.cell = Purkinje() # cell_template
          model.cell_regions = {"vm_soma": 0.0, "vm_NOR3": 0.0}
    Here cell_template = Purkinje() is the instantiated Python class of the
    NEURON model. prediction_dir_path is the path obtained by calling the
    check_and_make_directory() function; for eg.,
    check_and_make_directory("model-predictions", "cells", "PC2015Masoli")
    And "vm_soma", "vm_NOR3" etc ... are the variable number of arguments
    that represent NEURON cell properties.
    """
    dir_path = dir_path + os.sep
    #
    if response_type=="voltage_response":
        # create a container for storing/attaching the voltage responses
        # to the model
        model.predictions.update( { response_type: {} } )
        # get the times associated with each voltage response
        time = np.array( getattr( model.cell, "rec_t") )
        # loop through each cell region to save the prediction into
        # a .txt file and also attach the prediction into the model
        for cell_region, with_thresh in model.cell_regions.iteritems():
            # create an array of time and voltage responses
            t_vm_array = \
                    np.column_stack( ( time,
                                       np.array( getattr( model.cell,
                                                          cell_region ) )
                                        ) )
            # save the a_prediction into a .txt file
            file_name_full_path = dir_path + cell_region + ".txt"
            np.savetxt( file_name_full_path, t_vm_array, delimiter = ' ' )
            # attach the a_prediction to the model
            a_prediction = {cell_region: t_vm_array}
            model.predictions[response_type].update(a_prediction)
            #
            model.predicted_files_full_path.append(file_name_full_path)
            #
    elif response_type=="spike_train":
        for cell_region, with_thresh in model.cell_regions.iteritems():
            spikes = model.predictions[response_type][cell_region]
            file_name_full_path = dir_path + "spikes_" + cell_region + ".txt"
            np.savetxt( file_name_full_path, spikes )
            #
            model.predicted_files_full_path.append(file_name_full_path)
            #
    # save the file_name for possible reset
    #model.predicted_files_full_path.append(file_name_full_path)

# created 01 January 2018
def clone_method(m):
    if (sys.version_info > (3, 0)):
        # Python 3 code
        # import modules
        f = types.FunctionType( m.__code__,
                                m.__globals__,
                                name = m.__name__,
                                argdefs = m.__defaults__,
                                closure = m.__closure__ )
    else:
        # Python 2 code
        # import modules
        f = types.FunctionType( m.func_code,
                                m.func_globals,
                                name = m.func_name,
                                argdefs = m.func_defaults,
                                closure = m.func_closure )
    # wrap the method to f
    f = functools.update_wrapper(f, m)
    return f

# created 02 January 2018
def run_model(model_instance, runtime_parameters=None, stimulus_parameters=None):
    #model_instance.set_simulation_properties(runtime_parameters)
    #model_instance.set_stimulation_properties(stimulus_parameters)
    #model_instance.produce_voltage_response()
    try:
        model_instance.pid
    except AttributeError:
        print("AttributeError")
        model_instance.pid = os.fork()
    else:
        print("os._exit")
        os._exit(model_instance.pid)
        del model_instance.pid
    set_runtime_parameters(model_instance, runtime_parameters)
    if stimulus_parameters == None:
        pass
    else:
        inject_current(model_instance, stimulus_parameters, stim_type="IClamp")
    #model_instance.produce_voltage_response()
    model_instance.produce_spike_train()

#
#
