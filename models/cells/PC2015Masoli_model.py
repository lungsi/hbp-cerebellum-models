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
import copy

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
from ..simulation_manager import set_runtime_parameters as set_runtime
from ..simulation_manager import initialize_and_run_NEURON_model as irNm
from ..simulation_manager import save_predictions as sp
from ..simulation_manager import clone_method
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
    # AFTER the model is in the HBP Validation Framework Model catalog, set the generated uuid
    uuid = "22dc8fd3-c62b-4e07-9e47-f5829e038d6d"
    #
    #instance = None # for only ONE class instance and for reset()
    #
    def __init__(self):
        #
        # Initialize the class instance
        #if type(self).instance is None:
            # initialize if PurkinjeCell.instance does not exist
        #    type(self).instance = self
        #else: # raise error
        #    raise RuntimeError("Only one instance of 'PurkinjeCell' can exist at a time")
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
        self.cwd = os.getcwd() # this is the root
        self.path_to_files = self.cwd + os.sep + "models" + \
                        os.sep + "cells" + os.sep + \
                        "PC2015Masoli" + os.sep
        os.chdir(self.path_to_files) # change to path_to_files
        self.cell = Purkinje() # self.reset_cell = copy.deepcopy(self.cell)
        os.chdir(self.cwd)
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
        self.predicted_files_full_path = [] # keeps file names
        # =====specify cell_regions from which you want predictions======
        # created 22 Sept 2017
        self.cell_regions = {"vm_soma": 0.0, "vm_NOR3": 0.0}
        #
        print ("size of rec_t is "+ str(self.cell.rec_t.size()) +
               " and its current value is "+ str(h._ref_t[0]))
        print ("size of vm_soma is "+ str(self.cell.vm_soma.size()) +
               " and its current value is "+ str(self.cell.soma(0.5)._ref_v[0]))
        print ("size of vm_NOR3 is "+ str(self.cell.vm_NOR3.size()) +
               " and its current value is "+ str(self.cell.axonNOR3(0.5)._ref_v[0]))
    

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
        list_of_stimuli = []
        n = len(current_parameters) # number of currents
        # =============first create 'n' IClamps
        for i in range(n):
            # IClamp for each stimulus
            list_of_stimuli.append( h.IClamp(0.5, sec=self.cell.soma) )
            list_of_stimuli[i].amp = \
                    current_parameters["current"+str(i+1)]["amp"]
            list_of_stimuli[i].dur = \
                    current_parameters["current"+str(i+1)]["dur"]
            list_of_stimuli[i].delay = \
                    current_parameters["current"+str(i+1)]["delay"]
        return list_of_stimuli
      
    # +++++++++++++++++++++++++++++reset++++++++++++++++++++++++++++++++
    # created:  29 January 2018
    # modified: 
    # Note: This function resets the model by removing any stored data.
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def reset( self ):
        #for i in range(len(self.predicted_files_full_path)):
        #    os.remove(self.predicted_files_full_path[i])
        self.predictions = {}
        #del self.cell
        #self.cell = self.reset_cell
        #print h._ref_t
        #print h._ref_t[0]
        #h._ref_t[0] = 0.0
        #print self.cell.soma(0.5)._ref_v[0]
        #self.cell.soma(0.5)._ref_v[0] = 0.0
        #print self.cell.axonNOR3(0.5)._ref_v[0]
        #self.cell.axonNOR3(0.5)._ref_v[0] = 0.0
        #print h._ref_t
        #print h._ref_t[0]
        #self.cell.rec_t = self.cell.rec_t.remove(0, self.cell.rec_t.size()-1)
        #self.cell.vm_soma = self.cell.vm_soma.remove(0, self.cell.vm_soma.size()-1)
        #self.cell.vm_NOR3 = self.cell.vm_NOR3.remove(0, self.cell.vm_NOR3.size()-1)
        #self.cell.rec_t.record(h._ref_t)
        #self.cell.vm_soma.record(self.cell.soma(0.5)._ref_v)
        #self.cell.vm_NOR3.record(self.cell.axonNOR3(0.5)._ref_v)
        #h('proc init() {finitialize(v_init) nrnpython("myinit()")}')
        print('initializing...')
        # only need the following if states have been changed
        #if h.cvode.active():
        #    h.cvode.re_init()
        #else:
        #    h.fcurrent()
        #Fixed_step = h.CVode()
        #Fixed_step.active(0) #model doesn't work with variable time-step
        # Make all assigned variables (currents, conductances, etc)
        # consistent with the values of the states.
        #h.fcurrent()
        # Initializes the Vectors which are recording variables.
        # i.e. resize to 0 and append the current values of the variables.
        # This is done at the end of an finitialize() call but needs to be
        # done again to complete initialization if the user changes states or
        # assigned variables that are being recorded.
        #h.frecord_init()
        #h._ref_t[0] = 0.0
        #self.cell.soma(0.5)._ref_v[0] = -65.0
        #self.cell.axonNOR3(0.5)._ref_v[0] = -65.0
        #os.chdir(self.path_to_files) # change to path_to_files
        #self.cell = Purkinje() # self.reset_cell = copy.deepcopy(self.cell)
        #os.chdir(self.cwd)
        #self.cell.rec_t = h.Vector()
        #self.cell.vm_soma = h.Vector()
        #self.cell.axonNOR3 = h.Vector()
        #self.cell.rec_t.record(h._ref_t)
        #self.cell.vm_soma.record(self.cell.soma(0.5)._ref_v)
        #self.cell.vm_NOR3.record(self.cell.axonNOR3(0.5)._ref_v)
        self.cell.parallelcontext.gid_clear()
        #self.cell.parallelcontext = h.ParallelContext()
        self.pid = os.fork()
        print('intialization done')
        
    def reset_start( self ):
        self.pid = os.fork()
        
    def reset_exit( self ):
        os._exit(self.pid)
        
    # ----Class method----
    # PurkinjeCell()
    # pc = PurkinjeCell.instance
    # PurkinjeCell.reset()
    # pc = PurkinjeCell.instance
    #@classmethod
    #def reset(cls):
        # Clear PurkinjeCell.instance so that __init__ does not fail
    #    cls.instance = None
        # Call initialization
    #    cls.self = PurkinjeCell()
    
#
# ==========================================================================
