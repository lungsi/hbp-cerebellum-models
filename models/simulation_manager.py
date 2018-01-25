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
from datetime import datetime
from pynwb import NWBFile
import pynwb
import pkg_resources
from pynwb.icephys import CurrentClampSeries, CurrentClampStimulusSeries
from pynwb import get_manager
from pynwb.form.backends.hdf5 import HDF5IO


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
            np.savetxt( dir_path + "spikes_" + cell_region + ".txt", spikes )


def build_nwbfile( file_meta_data ):
    """
    Use case:
    file_meta_data = { "source": "Where is the data from?",
                       "session_description": "How was the data generated?",
                       "identifier": "a unique ID",
                       "session_start_time": str(time when recording began),
                       "experimenter": "name of the experimenter",
                       "experiment_description": "described experiment",
                       "session_id": "collab ID",
                       "institution": "name of the institution",
                       "lab": "name of the lab" }
    file_to_write = build_nwbfile( file_metadata )
    """
    file_to_write = NWBFile( source = file_meta_data["source"],
                             session_description = file_meta_data["session_description"],
                             identifier = file_meta_data["identifier"],
                             session_start_time = file_meta_data["session_start_time"],
                             file_create_date = str(datetime.now()),
                             version = str(pkg_resources.get_distribution("pynwb").version),
                             experimenter = file_meta_data["experimenter"],
                             experiment_description = file_meta_data["experiment_description"],
                             session_id = file_meta_data["session_id"],
                             institution = file_meta_data["institution"],
                             lab = file_meta_data["lab"] )
    return file_to_write


def construct_nwbepochs( nwbfile, epoch_meta_data ):
    """
    Use case:
    epoch_meta_data = { "epoch1": {"source": "where is this from?",
                                   "start": float, "stop": float,
                                   "description": "first epoch"},
                        "epoch2": {"source": "where is this from?",
                                   "start": float, "stop": float,
                                   "description": "second epoch"} }
    nwbfile, epoch_list = construct_nwbepochs( nwbfile, epoch_meta_data )
    """
    epoch_tags = ( nwbfile.identifier + "_epochs", )
    nwb_epochs_list = []
    for key in epoch_meta_data.keys():
        nwb_epochs_list.append(
                nwbfile.create_epoch ( name = key,
                                       source = epoch_meta_data[key]["source"],
                                       start = epoch_meta_data[key]["start"],
                                       stop = epoch_meta_data[key]["stop"],
                                       tags = epoch_tags,
                                       description = epoch_meta_data[key]["description" ) )
    return nwbfile, nwb_epochs_list

#
#
