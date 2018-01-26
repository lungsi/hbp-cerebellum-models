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
from pynwb.icephys import VoltageClampSeries, VoltageClampStimulusSeries
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
# modified 26 January 2018 Lungsi (0.2.0dev)
def save_predictions(nwbfile_details):
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
    nwbfile_to_write = build_nwbfile( nwbfile_details["file_meta_data"] )
    # create epochs and update the file with epoch
    epoch_electrodes_all_responses = {}
    for key in nwbfile_details["responses"].keys():
        # create epoch and update the created nwbfile
        epoch_meta_data = \
            nwbfile_details["responses"][key]["epoch_meta_data"]
        nwbfile_to_write, nwb_epoch_list = \
            construct_nwbepochs( nwbfile_to_write, epoch_meta_data )
        # create electrode and update the nwbfile
        electrode_meta_data = \
            nwbfile_details["responses"][key]["electrode_meta_data"]
        nwbfile_to_write, nwb_clamped_electrode = \
            construct_nwb_icelectrode( nwbfile_to_write,
                                       electrode_meta_data )
        # create timeseries NWB object
        ts_meta_data = \
            nwbfile_details["responses"][key]["ts_meta_data"]
        ts_nwb_object = \
            construct_nwb_timeseries_obj( ts_meta_data,
                                          nwb_clamped_electrode)
        # add the timeseries response to the file
        nwbfile_to_write.add_acquisition( ts_nwb_object,
                                          nwb_epoch_list )
        epoch_electrodes_all_responses.update(
            { key: {epoch_list: nwb_epoch_list,
                    clamped_electrode: nwb_clamped_electrode} } )
    # create Stimulus timeseries NWB object
    stimulus_ts_meta_data = nwbfile_details["stimulus"]["ts_meta_data"]
    clamped_electrode = \
        epoch_electrodes_all_responses["response1"]["clamped_electrode"]
    stimulus_ts_nwb_object = \
        construct_nwb_timeseries_obj( stimulus_ts_meta_data,
                                      clamped_electrode )
    # add the timeseries stimulus to the file
    nwbfile_to_write.add_stimulus(stimulus_ts_nwb_object)
    # write the nwbfile to a .h5 file in a chosen path
    io = HDF5IO( nwbfile_details["filename_w_dirpath"],
                 manager=get_manager(), mode="w" )
    io.write( nwbfile_to_write )
    io.close()


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
                                   "description": "second epoch"}
                        "epoch_tags": ("responseN_epochs",) }
    nwbfile, epoch_list = construct_nwbepochs( nwbfile, epoch_meta_data )
    """
    meta_wo_tags = { x: epoch_meta_data[x] for x in epoch_meta_data
                                           if x not in {"epoch_tags"} }
    nwb_epochs_list = []
    for key in meta_wo_tags.keys():
        nwb_epochs_list.append(
                nwbfile.create_epoch ( name = key,
                                       source = meta_wo_tags[key]["source"],
                                       start = meta_wo_tags[key]["start"],
                                       stop = meta_wo_tags[key]["stop"],
                                       tags = epoch_meta_data["epoch_tags"],
                                       description = meta_wo_tags[key]["description" ) )
    return nwbfile, nwb_epochs_list


def construct_nwb_icelectrode( nwbfile, electrode_meta_data ):
    """
    Use case:
    electrode_meta_data = { "name": "name of the electrode or use IClamp or IRamp",
                            "source": "which electrode of the clamp?",
                            "slice": "slice size of the tissue",
                            "seal": "seal used for recording or no seal",
                            "description": "describe recording or electrode, for eg., whole-cell, sharp, etc."
                            "location": "area, layer, stereotaxis coordinate or just choose one: soma, denrite, axon, etc.",
                            "resistance": "amount of resistance in the electrode (unit is Ohm)",
                            "filtering": "eg., 2.2Hz Bessel filter function",
                            "initial_access_resistance": "eg. nil",
                            "device": "device name" }
    nwbfile, clamped_electrode = construct_nwb_icelectrode( nwbfile, electrode_meta_data )
    """
    clamped_electrode = \
            nwbfile.create_intracellular_electrode(
                    name = electrode_meta_data["name"],
                    source = electrode_meta_data["source"],
                    slice = electrode_meta_data["slice"],
                    seal = electrode_meta_data["seal"],
                    description = electrode_meta_data["description"],
                    location = electrode_meta_data["location"],
                    resistance = electrode_meta_data["resistance"],
                    filtering = electrode_meta_data["filtering"],
                    initial_access_resistance = electrode_meta_data["initial_access_resistance"],
                    device = electrode_meta_data["device"] )
    return nwbfile, clamped_electrode


def construct_nwb_timeseries_obj( ts_meta_data, clamped_electrode ):
    """
    Use case:
    voltage_meta_data = { "type": "CurrentClampSeries",
                          "source": "Who is this from?",
                          "data": np.array( getattr( model.cell, "vm_soma" ) ),
                          "gain": 0.0,
                          "bias_current": 0.0,
                          "bridge_balance": 0.0,
                          "capacitance_compensation": 0.0,
                          "resolution": dt,
                          "conversion": 1000.0,
                          "timestamps": np.array( getattr( model.cell, "rec_t" ) ),
                          "starting_time": 0.0,
                          "rate": 1/dt,
                          "comment": "voltage response to current injection",
                          "description": "voltage response from the soma" }

    injection_meta_data = { "type": "CurrentClampStimulusSeries",
                          "source": "Who is this from?",
                          "data": model.predictions["vo,
                          "unit": "milliAmp",
                          "gain": 0.0,
                          "resolution": dt,
                          "conversion": 10.0**6,
                          "timestamps": np.array( getattr( model.cell, "rec_t" ) ),
                          "starting_time": 0.0,
                          "rate": 1/dt,
                          "comment": "soma current injection",
                          "description": "IClamp into soma" }
    tseries_vresponse = construct_nwb_timeseries_obj( voltage_meta_data,
                                                      clamped_electrode )
    tseries_currentinj = construct_nwb_timeseries_obj( injection_meta_data,
                                                       clamped_electrode )
    """
    ts_type = ts_meta_data["type"]
    if ts_type == "CurrentClampSeries":
        ts_object = \
            CurrentClampSeries(
                name = ts_meta_data["name"],
                source = ts_meta_data["source"],
                data = ts_meta_data["data"],
                unit = "milliVolt",
                electrode = clamped_electrode,
                gain = ts_meta_data["gain"],
                bias_current = ts_meta_data["bias_current"],
                bridge_balance = ts_meta_data["bridge_balance"],
                capacitance_compensation = ts_meta_data["capacitance_compensation"],
                resolution = ts_meta_data["resolution"],
                conversion = ts_meta_data["conversion"],
                timestamps = ts_meta_data["timestamps"],
                starting_time = ts_meta_data["starting_time"],
                rate = ts_meta_data["rate"],
                comment = ts_meta_data["comment"],
                description = ts_meta_data["description"] )
    #
    elif ts_type == "CurrentClampStimulusSeries":
        ts_object = \
            CurrentClampStimulusSeries(
                name = ts_meta_data["name"],
                source = ts_meta_data["source"],
                data = ts_meta_data["data"],
                unit = ts_meta_data["unit"],
                electrode = clamped_electrode,
                gain = ts_meta_data["gain"],
                resolution = ts_meta_data["resolution"],
                conversion = ts_meta_data["conversion"],
                timestamps = ts_meta_data["timestamps"],
                starting_time = ts_meta_data["starting_time"],
                rate =  ts_meta_data["rate"],
                comment = ts_meta_data["comment"],
                description = ts_meta_data["description"] )
    #
    elif ts_type == "VoltageClampSeries":
        # to be filled
        #ts_object = VoltageClampSeries()
    elif ts_type == "VoltageClampStimulusSeries":
        # to be filled
        #ts_object = VoltageClampStimulusSeries()
    #
    return ts_object  
#
#
