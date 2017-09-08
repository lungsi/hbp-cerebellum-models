# =============================================================================
# plot_manager.py
#
# created  30 August 2017 Lungsi
# modified 30 August 2017 Lungsi
#
# This py-file contains plot functions, initiated by
#
# from models import plot_manager
#
# and individual file_manager initiated by:
#
# 1. plot_manager.visualize_spikes ( model_name="PC2015Masoli",
#                                    region_of_interest="vm_soma" )
#    note: This utility plots the spikes from the desired region                
#          of the cell. This function reads the file
#          ~/model-predictions/cells/PC2015Masoli/spikes_vm_soma.txt
#
# 2. plot_manager.visualize_voltages ( model_name="PC2015Masoli",
#                                      region_of_interest="vm_soma" )
#    note: This utility plots the membrane voltage from the desired
#          region of the cell. This function reads the file
#          ~/model-predictions/cells/PC2015Masoli/vm_soma.txt
#
# =============================================================================

import numpy as np
from matplotlib import pyplot as plt

from .file_manager import get_prediction_file as gpf


def visualize_spikes( model_name = "CellYearAuthor",
                      region_of_interest = "vm_soma" ):
    """
    Use case: visualize_spikes ( model_name = "PC2015Masoli",
                                 region_of_interest = "vm_soma" )
    """
    # =====================Plot spikes from files====================
    #
    spike_file_name = "spikes_" + region_of_interest + ".txt"
    spikes_file_path = gpf( model_name = model_name,
                            file_name = spike_file_name )
    x = np.append( [0], np.loadtxt(spikes_file_path) )
    ymin = np.append( [0], np.zeros(len(x)) )
    ymax = np.append( [0], np.ones(len(x)) )
    #
    fig = plt.figure()
    plt.vlines(x, ymin, ymax, color='blue', linewidth=2)
    fig.suptitle( "Spike Train from " + region_of_interest
                   + ", " + model_name,
                   fontsize = 16 )
    plt.xlabel("Times (ms)", fontsize=14)
    plt.ylabel("All or None", fontsize=14)
    plt.yticks( np.arange(2), ("0", "1") )
    #fig.savefig("file_name.jpg")
    plt.show()
    # ===============================================================


def visualize_voltages( model_name = "CellYearAuthor",
                        region_of_interest = "vm_soma" ):
    """
    Use case: visualize_voltages( model_name = "PC2015Masoli",
                                  region_of_interest = "vm_soma" )
    """
    file_name = region_of_interest + ".txt"
    file_path = gpf( model_name = model_name,
                     file_name = file_name )
    data = np.loadtxt(file_path)
    time = data[:,0]
    volts= data[:,1]
    #
    fig = plt.figure()
    plt.plot(time, volts)
    fig.suptitle( "Voltage response from " + region_of_interest
                  + ", " + model_name,
                  fontsize = 16 )
    plt.xlabel("Times (ms)", fontsize=14)
    plt.ylabel("Voltage (mv)", fontsize=14)
    #fig.savefig("file_name.jpg)
    plt.show()


#def foo()
#
#
