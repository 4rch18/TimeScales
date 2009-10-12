# Author Michele Mattioni
# Wed Sep 16 12:26:40 BST 2009

import helpers 
    
if __name__ == "__main__":
        
    from optparse import OptionParser
    usage = "usage: %prog [options] path/to/storage"
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    
    
    if len(args) != 1:
        parser.error("Incorrect number of arguments")
        parser.usage()
    else:
        storage = args[0]
    
    from nrnvisio.controls import Controls
    controls = Controls()
    from neuron import h
    import neuronControl
    import helpers
    from neuronControl.spine import Spine
    
    # Loading the geometry of the neuron
    nrnSim = neuronControl.NeuronSim(mod_path="mod", hoc_path="hoc", 
                              spines=False, biochemical=False, 
                              biochemical_filename="biochemical_circuits/biomd183_noCalcium.eml")
    # We load without spines!
    l = helpers.Loader()
    sto = l.load(storage)
    
    # Loading in read_only mode in Neuronvisio
    controls.read_only(sto)
    
    # Picking up the spines
    for i, id in enumerate(sto.spines_id):
        spine_pos = sto.spines_pos[i]
        spine_parent_sec = sto.spines_parent[i]
        for sec in h.allsec():
            if sec.name() == spine_parent_sec:
                spine = Spine(id, biochemical=False) # Not loading E-cell
                spine.attach(sec, spine_pos, 0)
    # Attaching the vecRef_properly
    for sec in h.allsec():
        for vecRef in sto.vecRefs:
            if sec.name() == vecRef.sec_name:
                vecRef.sec = sec
                break
        
        
    
    
    