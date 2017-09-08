# =============================================================================
# PC2015Masoli_model.py
#
# created  01 August 2017 Lungsi
# modified 29 August 2017 Lungsi
#
# This py-file contains the class of the model.
#
# The naming structure of the model is as follows
# <UpperCaseLetters><Year><FirstAuthor>_model
# PC for Purkinje Cell, GoC for Golgi Cell and GrC for Granular Cell
#
# The class name is dependent on the UpperCaseLetters as follows:
# PC => PurkinjeCell
# GoC => GolgiCell
# GrC => GranularCell
#
# note: This file is imported in the __init__.py located here as
#       from . import PC2015Masoli_model as PC2015Masoli
#
#       This is not to be confused with the import command in this file
#       from PC2015Masoli.Purkinje import Purkinje
#       Here the Purkinje class is imported from the script file Purkinje.py
#       in the directory PC2015Masoli. The instantiated Purkinje class
#       is the cell template.
#
#       Apart from compiling the mod-files in the PC2015Masoli directory
#       almost all the files are the original author (modeller) version.
#       A few line were added in the Purkinje.py file to make sure that
#       the associated model files are within the path.
#
# =============================================================================

import os

from neuron import h
import sciunit
import numpy as np
from cerebunit.capabilities.cells.response import ProducesSpikeTrain
from cerebunit.capabilities.cells.response import ProducesElectricalResponse

#from ..file_manager import get_file_path as gfp
from ..file_manager import get_prediction_file as gpf
from ..file_manager import get_model_lib_path as gmlp
from ..file_manager import check_and_make_directory as cmdir
from ..model_manager import check_and_compile_model as ccm
from ..simulation_manager import check_capability_availability as cca
from ..simulation_manager import discover_cores_activate_multisplit as dcam
from ..simulation_manager import initialize_and_run_NEURON_model as irNm
from ..simulation_manager import save_predictions as sp
from ..signal_processing_manager import convert_vm_to_spike_train as getspikes
from PC2015Masoli.Purkinje import Purkinje


# ======================SciUNIT-CerebUNIT Based Model=======================
#
class PurkinjeCell( sciunit.Model, ProducesSpikeTrain,
                    ProducesElectricalResponse ):
    '''
    Use case: from models import cells
    pc = cells.PC2015Masoli.PurkinjeCell() # instantiate
    setup_parameters={"dt": 0.025, "celsius": 37, "tstop": 1000, "v_init": -65}
    pc.set_simulation_properties(setup_parameters)
    pc.produce_spike_train() # for produce_spike_train capability.
    pc.produce_voltage_response()
    -------------------------------------------
    PC2015Masoli model produces the following capabilities:
    produce_spike_train
    '''
    def __init__(self):
        #
        self.model_scale = "cells"
        self.model_name = "PC2015Masoli"
        # check that the NEURON model is compiled if not compile
        model_mod_path, model_lib_path = \
                gmlp( model_scale = self.model_scale,
                      model_name = self.model_name )
        ccm(model_mod_path, model_lib_path)
        print model_mod_path, model_lib_path, os.getcwd()
        #
        # load NEURON model library
        h.nrn_load_dll(model_lib_path)
        #
        # fixed time-step only
        Fixed_step = h.CVode()
        Fixed_step.active(0) #model doesn't work with variable time-step
        #
        # instantiate cell template
        #cwd = os.getcwd()
        #os.chdir(cwd + os.sep + "models" + os.sep + "cells" \
        #           + os.sep + "PC2015Masoli"
        self.cell = Purkinje()
        #os.chdir(cwd)  # reset to original directory
        #
        # discover no.cores in 1CPU & activate multisplit to use all cores
        dcam(h)
    

    # +++++++++++++++Model Capability: produce_spike_train++++++++++++++++
    # created:  03 August 2017
    # modified: 29 August 2017
    # Note: This function name should be the same as the method name in
    #       ProducesSpikeTrain.
    #       This function takes two arguments:
    #       cell_locations = list of string
    #       thresh = list of floats or integers FOR EACH cell_location
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def produce_spike_train( self, cell_locations=["vm_soma"],
                             thresh=[0.0] ):
        """
        Input: cell_locations=["vm_soma", "vm_NOR3"]
               thresh = [0.0, 0.0] (for peak detection)
               ====================removed======================
               signal_up_down=["above", "down"] (for inhibitory signals)
               =================================================
        Use case:
           pc.produce_spike_train( cell_locations=["vm_soma","vm_NOR3"],
                                   thresh=[0.0, 0.0] )
                                   ============removed==============
                                   signal_up_down=["above","down"] )
                                   =================================
        """
        #
        # ===================Get Voltage Response=======================
        # by calling produce_voltage_response
        # Input:  cell_locations=["vm_soma", "vm_NOR3", ...]
        # Output: self.prediction_dir_path and
        #         files in the path; vm_soma.txt, vm_NOR3.txt, ...
        #
        self.produce_voltage_response(cell_regions=cell_locations)
        # ==============================================================
        #
        print(ProducesSpikeTrain.__name__ + " has the method " + "produce_spike_train" + " ... \n")
        #
        # ============Extract spikes from Voltage Response==============
        # for each location get the file_path containing voltage response
        # based on this extract the spikes in the form of array of times
        # when the spikes occured.
        # These times @ spike occurrences are written into .txt file.
        #
        for i in range(len(cell_locations)):
            # load and extract time stamps and corressponding voltages
            #file_path = gfp( dir_names=["model-predictions", "cells",
            #                            "PC2015Masoli"],
            #                 file_name=cell_locations[i] + ".txt" )
            file_path = gpf( model_name=self.model_name,
                             file_name=cell_locations[i] + ".txt" )
            # convert voltage response into analog signal and get spikes
            spikes = getspikes( path_to_file=file_path,
                                theta=thresh[i] )
            # save the spikes into .txt file (spikes_vm_soma.txt)
            np.savetxt( self.prediction_dir_path + os.sep + \
                        "spikes_" + cell_locations[i] + ".txt",
                        spikes )
        # ===============================================================
        print " Done!"


    # ++++++++++++Model Capability: produce_voltage_response+++++++++++++
    # created:  03 August 2017
    # modified: 27 August 2017
    # Note: This function name should be the same as the method name in
    #       ProducesElectricalResponse.
    #       This function takes two arguments:
    #       cell_regions = list of string
    #       [NB: cell_regions is the same as cell_locations in
    #            produce_spike_train]
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def produce_voltage_response(self, cell_regions=["vm_soma", "vm_NOR3"]):
        print "Running " + self.model_name + " " + self.model_scale + " ... \n",
        #
        # ===========Implement produce_voltage_response capability============
        # 
        cca( capability_name = "produce_voltage_response",
             CerebUnitCapability = ProducesElectricalResponse ) # check capab.
        # ====================================================================
        #
        # =================Setup-Initialize-Run Simulation====================
        #
        #self.set_simulation_properties() # set-up simulation time
        irNm(h)                          # initialize & run NEURON
        # ====================================================================
        #
        # =============Save predictions in "model_predictions"================
        #
        self.prediction_dir_path = cmdir( "model-predictions",
                                           self.model_scale,
                                           self.model_name )
        sp(self.cell, self.prediction_dir_path, cell_regions)
        # ====================================================================
        print " Done!"
    

    # +++++++++++++++++++++set_simulation_properties++++++++++++++++++++
    # created:  03 August 2017
    # modified: 31 AUgust 2017
    # Note: This function is NOT model capability function.
    #       This function takes four arguments:
    #       time_step = 
    #       temp =
    #       t_final =
    #       v_init =
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_simulation_properties( self, setup_parameters ):
        h.dt = setup_parameters["dt"]
        h.celsius = setup_parameters["celsius"]
        h.tstop = setup_parameters["tstop"]
        h.v_init = setup_parameters["v_init"]


    # +++++++++++++++++++++set_stimulation_properties++++++++++++++++++++
    # created:  01 September 2017
    # modified: 
    # Note: This function is NOT model capability function.
    #       This function takes four arguments:
    #       time_step = 
    #       temp =
    #       t_final =
    #       v_init =
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_stimulation_properties( self, current_parameters ):
        stimulus = []
        n = len(current_parameters) # number of currents
        # =============first create 'n' IClamps
        for i in range(n):
            stimulus.append( h.IClamp(0.5, sec=self.cell.soma) )
            stimulus[i].amp = current_parameters["current"+str(i)]["amp"]
            stimulus[i].dur = current_parameters["current"+str(i)]["dur"]
            stimulus[i].delay = \
                    current_parameters["current"+str(i)]["delay"]
    
#
# ==========================================================================
