# =============================================================================
# signal_processing_manager.py
#
# created  29 August 2017 Lungsi
# modified 29 August 2017 Lungsi
#
# This py-file contains functions, initiated by
#
# from models import signal_processing_manager
#
# and individual file_manager initiated by:
#
# 1. signal_processing_manager.convert_vm_to_spike_train
#            ( path_to_file=
#                "/model-predictions/cells/PC2015Masoli/vm_soma.txt"
#              theta=0.0 )
#    note: This loads the vm_soma.txt and based on the magnitude of
#          theta, vm > theta => spike and the corresponding time is
#          stamped. Therefore, all the time-stamps representing
#          times when spikes occurred are written in spikes_vm_soma.txt
#          NB: for negative membrane voltages the threshold is
#              determined not only by the magnitude of theta but
#              also the sign of theta.
#
# =============================================================================

import numpy as np
from neo.core import IrregularlySampledSignal as iss
from elephant.spike_train_generation import peak_detection as pd
from quantities import mV


def convert_vm_to_spike_train( path_to_file="/file/path", theta=0.0):
    """
    Use case: convert_vm_to_spike_train()
    """
    # ============Extract spikes from Voltage Response==============
    # for each location load the file containing voltage response
    # the file is such that 1st column is time stamps and
    # 2nd column is the corressponding voltages
    # Neo's IrregularlySampledSignal (iss) is used to convert the
    # voltage response into analog signal.
    # Neo's peak_detection (pd) is used to extract the spikes from
    # the analog signal. These times @ spike occurrences are
    # written into a .txt file.
    #
    #signal_sign = [ "above" if np.sign(x)==0 or 0.0 or 1.0 or 1
    #                else "below"
    #                for x in [theta] ][0]
    #
    signal_sign = [ "above" if np.sign(x)==0 or 0.0 or 1.0 or 1
                    else "below"
                    for x in [theta] ][0]
    data = np.loadtxt( path_to_file )
    column_time = data[:,0]
    column_volts= data[:,1]
    # convert voltage response into analog signal and get spikes
    signal = iss( column_time, column_volts, units='mV', time_units='ms' )
    spikes = pd( signal, threshold=np.array(theta)*mV,
                 sign=signal_sign, format=None )
    return spikes
    # ===============================================================


#def foo()
#
#
