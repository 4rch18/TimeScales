# Author: Michele Mattioni
# Fri Feb  4 15:03:02 GMT 2011

import sys
import os
import numpy as np

import matplotlib.pyplot as plt

from helpers.loader import Loader
try:
    import ecellControl.ecellManager as eC
except ImportError:
    pass


class StimulPlotter():
    """Helps to plot stimuli"""
    
    def __init__(self):
        pass
    
    def build_stimul_vec(self, time, stimul, height_in_the_graph):
        """Return a masked array which has `height_in_the_graph` value
        for each point recorded in stimul array.
        
        time - the time array of the simulation
        stimul - the synvecRef vectors with the synapstic inputs
        height_in_graph"""
        
        inputs_event = np.zeros_like(time)
        indxs = np.searchsorted(time, stimul)
        inputs_event[indxs] = height_in_the_graph
        masked = np.ma.masked_where(inputs_event == 0, inputs_event)
        return masked
    
    def plot_input(self, spine, manager, style='k.', height_in_the_graph=-88):
        
        spine += '_psd'
        stimul = manager.get_vector(spine, 'stimul_ampa', 'SynVecRef')
        
        if stimul is None:
            print "Error - Stimul not Plotted. No stim found for %s." %spine
        else:
            time = manager.groups['t']
            print "Buiding stim array for %s" %spine
            m_array = self.build_stimul_vec(time, stimul, height_in_the_graph)
            plt.plot(time, m_array, 'k.', label = "stimul")
            return m_array

class EcellPlotter():
    
    def plot_timeCourses(self, timeCourses, save=False, 
                        dir=None, name='test_spine', x_lims=None):
         """Plot the default timecourses"""
         import matplotlib.pyplot as plt
         ca_tc = timeCourses['ca'] 
         plt.figure()
         plt.plot(ca_tc[:,0], ca_tc[:,1], label="Calcium")
         plt.xlabel("Time [s]")
         if x_lims:
             plt.xlim(x_lims)
         plt.legend(loc=0)
         
         if save :
             filename = name +"_caInput.png"
             plt.savefig(os.path.join(dir, filename))
             print "figure saved in: %s" % os.path.join(dir, filename)
         
         vars = ['PP2Bbar', 'CaMKIIbar', 'PP1abar', 'AMPAR', 'AMPAR_P']
         
         for var in vars:
             plt.figure()
             var_tc = timeCourses[var]
             lbl = name + '_' + var
             plt.plot(var_tc[:,0], var_tc[:,1], label=lbl)
             plt.xlabel("Time [s]")
             if x_lims:
                 plt.xlim(x_lims)
             plt.legend(loc=0)
         
             if save :
                 filename = name + "_" + var + ".png"
                 plt.savefig(os.path.join(dir, filename))
                 print "figure saved in: %s" % os.path.join(dir, filename) 
    
    def plot_weight(self, timecourses, dir=None):
        import matplotlib.pyplot as plt
        scaled_CaMKII = []
        time = timecourses['AMPAR'][:,0] # time equal for everything
    
    
    
        plt.figure()
        plt.plot(time, timecourses['AMPAR_P'][:,1], label='AMPAR_P')
        #plt.plot(time, weight_baseline, label='w_b')
        title = "AMPA weight, calculated from E-Cell"
        plt.title(title)
        plt.legend(loc=0)
        if dir is not None:
            plt.savefig(os.path.join(dir, "weight.png"))
        plt.plot(time, timecourses['AMPAR'][:,1], label='AMPAR')
        plt.legend(loc=0)
        if dir is not None:
            plt.savefig(os.path.join(dir, "weight_both.png"))
            
    
    def plot_var(self, timeCourses, var):
        "Plot the variable in the current figure"
        var_tc = timeCourses[var]
        lbl = var
        plt.plot(var_tc[:,0], var_tc[:,1], label=lbl)
        plt.xlabel("Time [s]")
        plt.legend(loc=0)


class DoublePlotter():
    "plot both electrical and biochemical in one graph."
    def plot_double_axes(self, manager, spine, el_var, bio_var, bio_group):
        """
        Plot a double axes figure with the variables as argument, 
        return a tuple with the two axes used.
        
        Param
        -----
        manager - neuronvisio manager
        spine - spine to plot
        el_var - electrical variable to plot
        bio_var - biochemical variable to plot
        bio_group - group where the Ref is part of (e.g VecRef, 
                    SynVecRef, YourRef)
        """
        ax1 = plt.subplot(111)
        sec = spine + '_head'
        vec = manager.get_vector(sec, el_var)
        t = manager.groups['t']
        label = sec + "_" + el_var
        plt.plot(t, vec, label=label)
        
        # plotting the second one
        vec_bio = manager.get_vector(sec, bio_var, group=bio_group)
        t2 = manager.groups[bio_group]
        t2_ms = t2/1e3 #scaling to ms
        label = sec + "_" + bio_var
        ax2 = plt.twinx() 
        plt.plot(t2_ms, vec_bio, label=label)
        return (ax1, ax2)

if __name__ == "__main__":

    if len(sys.argv) == 2:
        
        filename = sys.argv[1]
        l = Loader()
        ecp = EcellPlotter()
        timecourses = l.load(filename)
        ecp.plot_timeCourses(timecourses, name='test_spine')
        print "Time courses loaded in 'timecourses' object. Easy plotting \n\
        with 'ecp' object. Have fun."
        plt.show()
    
    else:
        print "Tell me which file with ecell Timeseries to load."
        print "visualizatorBiochemical.py path/to/timecourses\n"
