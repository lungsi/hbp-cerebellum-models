# =============================================================================
# PC2015Masoli_model.py
#
# created  01 August 2017 Lungsi
#
# This py-file contains the class of the model.
# The template of the model in the directory PC2015Masoli/
# is based on http://dx.doi.org/10.3389/fncel.2015.00047
# available in
# https://senselab.med.yale.edu/ModelDB/showmodel.cshtml?model=229585
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
from cerebunit.capabilities.cells.response import ProducesSpikeTrain, ProducesElectricalResponse
from cerebunit.capabilities.cells.knockout import CanKOAISChannels, CanKOCav2pt1Channels
from cerebunit.capabilities.cells.morphology import CanDisconnectDendrites
# below two are needed to convert the voltage_response to spike_train
from quantities import mV
from elephant.spike_train_generation import peak_detection as pd

#from ..file_manager import get_file_path as gfp
from ..file_manager import get_prediction_file as gpf
from ..file_manager import get_model_lib_path as gmlp
from ..file_manager import check_and_make_directory as cmdir
from ..model_manager import check_and_compile_model as ccm
from ..simulation_manager import check_capability_availability as cca
from ..simulation_manager import discover_cores_activate_multisplit as dcam
from ..simulation_manager import initialize_and_run_NEURON_model as irNm
from ..simulation_manager import save_predictions as sp
#from ..signal_processing_manager import convert_vm_to_spike_train_from_file as getspikes
from ..signal_processing_manager import convert_voltage_response_to_spike_train as getspikes
from PC2015Masoli.Purkinje import Purkinje


# ======================SciUNIT-CerebUNIT Based Model=======================
#
class PurkinjeCell( sciunit.Model,
                    ProducesSpikeTrain,
                    ProducesElectricalResponse,
                    CanKOAISChannels,
                    CanKOCav2pt1Channels,
                    CanDisconnectDendrites ):
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
        #print model_mod_path, model_lib_path, os.getcwd()
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
        #
        # =========attributed inherited from sciunit.Model===============
        # pc.name defaults to class name, i.e, PurkinjeCell
        self.name = "Masoli et al. 2015 model of PurkinjeCell"
        self.description = "Masoli et al. 2015 model of PurkinjeCell (PC) and published in 10.3389/fncel.2015.00047 This is general PC model unlike special Z+ or Z- models. The model is based on adult (P90 or 3 months) Guinea pig. PC in younger ones are not mature and they grow until P90. This model is the SciUnit wrapped version of the NEURON model in modelDB accession # 229585."
        #
        # =========model predictions attached to the model object========
        # Note: this is not part of inherited attributes from sciuni.Model
        self.predictions = {}  # added 21 Sept 2017
        # =====save the predictions in model-predictions subfolders======
        self.prediction_dir_path = cmdir( "model-predictions",
                                           self.model_scale,
                                           self.model_name )
        # =====specify cell_regions from which you want predictions======
        # created 22 Sept 2017
        self.cell_regions = {"vm_soma": 0.0, "vm_NOR3": 0.0}
    

    # +++++++++++++++Model Capability: produce_spike_train++++++++++++++++
    # created:  03 August 2017
    # modified: 22 September 2017
    # Note: This function name should be the same as the method name in
    #       ProducesSpikeTrain.
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def produce_spike_train( self ):
        """
        Use case:
           by default
           pc.produce_spike_train()
           customize
           pc.cell_regions = {"vm_soma": 0.0, "vm_NOR3": 0.0} # default
           # format is key=> cell region; value=> threshold
           # now run
           pc.produce_spike_train()
        """
        #
        # ===================Get Voltage Response=======================
        # by calling produce_voltage_response
        # Output: self.prediction_dir_path and
        #         files in the path; vm_soma.txt, vm_NOR3.txt, ...
        #
        self.produce_voltage_response()
        # ==============================================================
        #
        print(ProducesSpikeTrain.__name__ + " has the method " + "produce_spike_train" + " ... \n")
        #
        # ====convert voltage response predictions into spike trains=====
        #self.spikes_from_all_regions = {}
        getspikes( self ) # this also attaches the predictions
        # ====save the prediction into a text file
        sp(self, "spike_train", self.prediction_dir_path)
        # ===============================================================
        print " Done!"


    # ++++++++++++Model Capability: produce_voltage_response+++++++++++++
    # created:  03 August 2017
    # modified: 22 September 2017
    # Note: This function name should be the same as the method name in
    #       ProducesElectricalResponse.
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def produce_voltage_response( self ):
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
        sp(self, "voltage_response", self.prediction_dir_path)
        # ====================================================================
        #
        print " Done!"
    

    # +++++++++++++++Model Capability: ko_AIS_channels+++++++++++++++++
    # created:  26 September 2017
    # modified: 
    # Note: This function name should be the same as the method name in
    #       CanKOAISChannels.
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def ko_AIS_channels( self ):
        #
        # ===============Implement ko_AIS_channels capability=================
        # 
        cca( capability_name = "ko_AIS_channels",
             CerebUnitCapability = CanKOAISChannels ) # check capab.
        #
        self.cell.axonAIS.pcabar_Cav3_1 = 0
        self.cell.axonAIS.gbar_Nav1_6 = 0
        self.cell.axonAIS.pcabar_Cav2_1 = 0
        # ====================================================================
        #print " Done!"
    

    # +++++++++++++++Model Capability: ko_Cav2_1_channels++++++++++++++++
    # created:  26 September 2017
    # modified: 
    # Note: This function name should be the same as the method name in
    #       CanKOCap2pt1Channels.
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def ko_Cav2_1_channels( self ):
        #
        # ==============Implement ko_Cav2_1_channels capability===============
        # 
        cca( capability_name = "ko_Cav2_1_channels",
             CerebUnitCapability = CanKOCav2ptChannels ) # check capab.
        # soma
        self.cell.soma.pcabar_Cav2_1 = 0
        # AIS
        self.cell.axonAIS.pcabar_Cav2_1 = 0
        # dendrite
        for d in self.cell.dend:
            d.pcabar_Cav2_1 = 0
        # Node of Ranviers
        self.cell.axonNOR.pcabar_Cav2_1 = 0
        self.cell.axonNOR2.pcabar_Cav2_1 = 0
        self.cell.axonNOR3.pcabar_Cav2_1 = 0
        # Collaterals
        self.cell.axoncoll.pcabar_Cav2_1 = 0
        self.cell.axoncoll2.pcabar_Cav2_1 = 0
        # ====================================================================
        #print " Done!"
    

    # +++++++++++++++Model Capability: disconnect_all_dendrites++++++++++++++++
    # created:  03 October 2017
    # modified: 
    # Note: This function name should be the same as the method name in
    #       CanDisconnectDendrites.
    #       This function disconnects all dendrite sections from its parents
    #       NOT JUST FROM soma.
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def disconnect_dendrites_from_soma( self ):
        #
        # ============Implement disconnect_all_dendrites capability============
        # 
        cca( capability_name = "disconnect_dendrites_from_soma",
             CerebUnitCapability = CanDisconnectDendrites ) # check capab.
        #
        #for d in self.cell.dend:
        #    if h.SectionRef(sec = d).has_parent != 0:
        #        h.disconnect(sec = d)
        h.disconnect(sec = self.cell.dend[0])
        # ====================================================================
        #print " Done!"


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
    def set_stimulation_properties( self, current_parameters ):
        stimulus = [] # list of stimuli
        n = len(current_parameters) # number of currents
        # =============first create 'n' IClamps
        for i in range(n):
            # IClamp for each stimulus
            stimulus.append( h.IClamp(0.5, sec=self.cell.soma) )
            stimulus[i].amp = current_parameters["current"+str(i+1)]["amp"]
            stimulus[i].dur = current_parameters["current"+str(i+1)]["dur"]
            stimulus[i].delay = current_parameters["current"+str(i+1)]["delay"]
        return stimulus
    
#
# ==========================================================================
