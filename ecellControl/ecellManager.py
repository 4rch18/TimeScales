# Author Michele Mattioni
# Fri Jan 30 15:57:01 GMT 2009

import ecell.Session
import ecell.ecs
import ecell.config
import ecell.emc
import os
import numpy
import pylab

class EcellManager():
    """Control and instatiate the ecell simulator embedding it in an handy python object"""
    
    def __init__(self, filename="../biochemical_circuits/biomd183.eml"):
        ecell.ecs.setDMSearchPath( os.pathsep.join( ecell.config.dm_path ) )
        self.sim = ecell.emc.Simulator()
        self.ses = ecell.Session.Session(self.sim)
        
        # Load the model
        self.ses.loadModel(filename)
        self.molToTrack = ('ca','moles_bound_ca_per_moles_cam',
                           'Rbar','PP2Bbar','CaMKIIbar')
        # Tracking the calcium
        self.ca =  self.ses.createEntityStub( 'Variable:/Spine:ca' )
        self.CaMKIIbar = self.ses.createEntityStub( 'Variable:/Spine:CaMKIIbar' )
        
        
    def createLoggers(self):
        """Create the logger to track the speces"""
        loggers = {}
        #log = ecell.LoggerStub()
        
        for mol in self.molToTrack:
            
            loggers[mol]  = self.ses.createLoggerStub( "Variable:/Spine:" + mol + ":Value" )
            loggers[mol].create() # This creat the Logger Object in the backend
        
        self.loggers = loggers
        
    
    def calcium_peak(self, k_value, duration):
        """
        Mimic the calcium peak
        
        :Parameters
            k_value: the rate of calcium to enter
            duration: Duration of the spike
        """
        
        basal = self.ca_in['k']
        self.ca_in['k'] = k_value
        self.ses.run(duration)
        self.ca_in['k'] = basal
        
    def calciumTrain(self, spikes=30, interval=0.1):
        """Create a train of calcium with the specified number of spikes and interval
        
        :Parameter
            spikes: number of spikes
            interval: Interval between spikes
        """
        for i in range(spikes):
            self.calcium_peak(4.0e8, # Magic number from Lu
                         0.00001 #Really fast spike to avoid the overlap
                         )
            self.ses.run(interval)
    
    def plotTimeCourses(self, batch=False, dir=None):
        """Plot the default timecourses"""
        ca_tc = self.timeCourses['ca'] 
        pylab.figure()
        pylab.plot(ca_tc[:,0], ca_tc[:,1], label="Calcium")
        pylab.xlabel("Time [s]")
        pylab.legend(loc=0)
        
        if batch :
            pylab.savefig(os.path.join(dir, "caInput.png"))
        
        bars = ['PP2Bbar', 'CaMKIIbar']
        pylab.figure()
        for bar in bars:
            bar_tc = self.timeCourses[bar]
            pylab.plot(bar_tc[:,0], bar_tc[:,1], label=bar)
            pylab.xlabel("Time [s]")
            pylab.legend(loc=0)
        
        if batch :
            pylab.savefig(os.path.join(dir, "PP2B_and_CaMKII_activation.png"))
        else:
            pylab.show()
        
    def converToTimeCourses(self):
        timeCourses = {}
        for key in self.loggers:
            timeCourses[key] = self.loggers[key].getData()
        
        self.timeCourses = timeCourses
        

        
##############################################
# Testing method

def testCalciumTrain(filename="../biochemical_circuits/biomd183.eml"):
    """Run a test simulation wit a train of calcium input"""
    
    print "Test the results of a train of calcium"""
    ecellManager = EcellManager(filename)
    ecellManager.createLoggers()
    ecellManager.ca_in = ecellManager.ses.createEntityStub('Process:/Spine:ca_in')
    print "Model loaded, loggers created. Integration start."
    ecellManager.ses.run(200)
    print "Calcium Train"
    ecellManager.calciumTrain()
    ecellManager.ses.run(400)
    ecellManager.converToTimeCourses()
    print "CalciumTrain Test Concluded\n##################"
    return ecellManager
    




def testChangeCalciumValue(interval, caValue=7, filename="../biochemical_circuits/biomd183_noCalcium.eml"):
    """Run a test simulation changing the calcium value on the fly"""
    print "Show case of the possibilities to change the level of calcium on the fly"
    ecellManager = EcellManager(filename)
    ecellManager.createLoggers()
    print "Loggers created"
    print "Running with the updating interval of : %f" %interval
    
    tstop = 150
    while(ecellManager.ses.getCurrentTime() < tstop):
        ecellManager.ca['Value'] = caValue
        ecellManager.ses.run(interval)
        #ecellManager.ses.run(1)
        #print ecellManager.ses.getCurrentTime()
    
    print "immision of Calcium"
    print "Value of Calcium %f" %ecellManager.ca.getProperty('Value')
    spikes = 4
    for i in range(spikes):
        ecellManager.ca['Value'] = 7200
        ecellManager.ses.run(0.020)
        ecellManager.ca['Value'] = caValue
        ecellManager.ses.run(0.010)
    
    tstop = tstop+500
    while(ecellManager.ses.getCurrentTime() < tstop):
        ecellManager.ca['Value'] = caValue
        ecellManager.ses.run(interval)
        #ecellManager.ses.run(1)
        #print ecellManager.ses.getCurrentTime()
        
    ecellManager.converToTimeCourses()
    print "ChangeCalciumValue Test Concluded\n##################"
    return ecellManager
        
if __name__ == "__main__":
    
    from ioHelper import *
    import os
    from optparse import OptionParser
    usage= "usage: %prog [options] interval.\n\
    Run the simulator using the interval [s] to update the calcium between different run"
    parser = OptionParser(usage)
    parser.add_option("-s", "--save", action="store_true", 
                      help= "If True save the graphs and the log")
    parser.add_option("-v", "--caValue", 
                      help= "The value of the calcium to pump into the system\
                      at each interval")
    (options, args) = parser.parse_args()
     
    
    if len(args) != 1:
        parser.error("Incorrect number of arguments")
        parser.usage()
    else:
        interval = float(args[0])
        print "Interval %f, Save option %s" %( interval, options.save)
    
    ## Setting the backend
    import matplotlib
    if options.save == True:
        try:
            import cairo
            matplotlib.use('Cairo')
            print "Switching backend to Cairo. Batch execution"
        except:
            matplotlib.use('Agg')
            print "Switching backend to Agg. Batch execution"
    
         
    ioH = IOHelper(prefix=os.getcwd())
    if hasattr(options, "caValue"):
        ecellManager = testChangeCalciumValue(interval, caValue=options.caValue)
    else:
        ecellManager = testChangeCalciumValue(interval)
    #ecellManager = testCalciumTrain()
    
    if options.save == True:
        dir = ioH.saveObj(ecellManager.timeCourses, "timeCourses")
        ecellManager.plotTimeCourses(batch=options.save, dir=dir)
        f = open(os.path.join(dir, 'log.txt'), 'w') 
        f.write("Test of the supply of the calcium to the biochemical model\n\
        Interval used in this simulation: %f\n" % (interval))
        f.close()
    else:
        ecellManager.plotTimeCourses()