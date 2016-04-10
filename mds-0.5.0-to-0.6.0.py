#!/usr/bin/env python

import os
import json

import mdsynthesis as mds
import MDAnalysis as mda

description = """Make a MDSynthesis 0.6.0 Sim from a pre-release Sim.

Prior to the first official release of MDSynthesis, a Sim could carry multiple
universe definitions. This was removed in favor of a Sim having only a single
universe, and the schema for the state file of a Sim changed as well.

This script will take a universe name and a single Sim state file as input, and
will produce a Sim with that named universe as its defined universe. Additional
Sims will be nested within for each additional universe definition in the
original. 

So if we had a Sim called "ADK" with three universe definitions "main",
"fitted", "no water", we could run:

  python mds-0.5.0-to-0.6.0.py main ADK/Sim.<uuid>.json

and we would go from a directory with:

  ADK/
      Sim.<uuid>.json

to a directory that looks like:

  ADK/
      Sim.<uuid>.json
      Sim.<uuid>.json.old

      fitted/
          Sim.<uuid>.json

      no water/
          Sim.<uuid>.json

Where the top-level Sim features the universe "main" as its universe, and the
nested ones have the other universe definitions. The names of universe
definitions must be valid directory names for this to work.

.. note:: The original Sim file will be appended with ".old" and left in the
          directory. It is harmless to leave it, but it is left untouched in
          case this script fails.

Defined atom selections for each universe will be preserved along the way, and
placed in the corresponding Sim.

"""

if __name__ == '__main__':
    
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    
    parser = ArgumentParser(description=description,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('topuniverse', help='Name of universe definition to use for top-level Sim')
    parser.add_argument('simfile', help='JSON state file for Sim to convert')

    args = parser.parse_args()

    newstate = dict()
    
    ## move the old state file to a name that MDS won't catch
    oldstatefile = args.simfile + '.old'
    os.rename(args.simfile, oldstatefile)

    with open(oldstatefile, 'r') as f:
        oldstate = json.load(f)

    ## grab datreant components first
    newstate['tags'] = oldstate['tags']
    newstate['categories'] = oldstate['categories']

    ## now, mdsynthesis surgery
    newstate['mdsynthesis'] = dict()

    topdir = os.path.dirname(os.path.abspath(oldstatefile))

    if args.topuniverse not in oldstate['mds']['universes'].keys():
        raise ValueError("universe '{}' not present "
                         "in given Sim".format(args.topuniverse))

    ## we build a new Sim for each stored Universe
    for uname in oldstate['mds']['universes'].keys():

        # if this is the selected universe, we make this the top-level Sim
        if args.topuniverse == uname:
            sim = mds.Sim(topdir)
            topstatefile = sim.filepath
        else:
            sim = mds.Sim(os.path.join(topdir, uname))

        # deposit tags, categories in each Sim
        sim.tags = oldstate['tags']
        sim.categories = oldstate['categories']

        # get absolute paths to files
        topabs, toprel = oldstate['mds']['universes'][uname]['top']
        trajabs = [x[0] for x in oldstate['mds']['universes'][uname]['traj']]

        # use absolute paths to define the universe for the sim
        sim.universedef._set_topology(topabs)
        sim.universedef._set_trajectory(trajabs)

        # get resnums if present; don't care if fails
        try:
            resnums = oldstate['mds']['universes'][uname]['resnums']
        except:
            pass
        else:
            sim.universedef._set_resnums(resnums)

        # grab atom selections
        for selname, sel in oldstate['mds']['universes'][uname]['sels'].items():
            sim.atomselections[selname] = sel

    ## make top-level state file same name (and uuid) as original
    os.rename(topstatefile, args.simfile)
