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


def initialize_and_run_NEURON_model(h):
    """
    Use case: initialize_and_run_NEURON_model(h)
    where h is a module; from neuron import h.
    """
    h.finitialize()
    start_time = time.clock()
    h.run()
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
    Use case: save_predictions(model, model.prediction_dir_pat)
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
    if response_type=="voltage_response":
        model.predictions.update( { response_type: {} } )
        time = np.array( getattr( model.cell, "rec_t") )
        for cell_region, with_thresh in model.cell_regions.iteritems():
            t_vm_array = \
                    np.column_stack( ( time,
                                       np.array( getattr( model.cell,
                                                          cell_region ) )
                                        ) )
            # save the a_prediction into a .txt file
            np.savetxt( dir_path + cell_region + ".txt",
                        t_vm_array,
                        delimiter = ' ' )
            # attach the a_prediction to the model
            a_prediction = {cell_region: t_vm_array}
            model.predictions[response_type].update(a_prediction)
            #
    elif response_type=="spike_train":
        for cell_region, with_thresh in model.cell_regions.iteritems():
            spikes = model.predictions[response_type][cell_region]
            np.savetxt( dir_path + "spikes+" + cell_region + ".txt", spikes )

#
#
