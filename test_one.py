from __future__ import print_function
from __future__ import absolute_import

######################################################################
# This file copyright the Georgia Institute of Technology
#
# Permission is given to students to use or modify this file (only)
# to work on their assignments.
#
# You may NOT publish this file or make it available to others not in
# the course.
#
######################################################################

# python modules
import argparse
import math
import sys

# project files
import asteroid
import bounds
import craft
import pilot
import runner
import cases

from text_display import TextRunnerDisplay
try:
    from turtle_display import TurtleRunnerDisplay
except ImportError as e:
    sys.stderr.write('turtle display not available, using text instead\n')
    TurtleRunnerDisplay = lambda h,w: TextRunnerDisplay()

def display_for_name( dname ):

    if dname == 'turtle':
        return TurtleRunnerDisplay(800,800)
    elif dname == 'text':
        return TextRunnerDisplay()
    else:
        return runner.BaseRunnerDisplay()

def case_params( case_num ):
    return cases.index[case_num]

def run_method( method_name ):
    if method_name == 'estimate':
        return runner.run_estimation
    elif method_name == 'navigate':
        return runner.run_navigation
    else:
        raise RuntimeError('unknown method %s' % method_name)

def run_kwargs( params ):

    asteroids = [ asteroid.Asteroid( **kwargs )
                  for kwargs in params['asteroids'] ]

    in_bounds = bounds.BoundsRectangle( **params['in_bounds'] )

    goal_bounds = bounds.BoundsRectangle( **params['goal_bounds'] )

    # TODO: rename to margin?
    min_dist = params['min_dist']

    ret = { 'field': asteroid.AsteroidField( asteroids = asteroids ),
            'craft_state': craft.CraftState( **( params['initial_craft_state'] ) ),
            'in_bounds': in_bounds,
            'goal_bounds': goal_bounds,
            'noise_sigma': params['noise_sigma'],
            'min_dist': min_dist,
            'pilot': pilot.Pilot( min_dist  = min_dist,
                                  in_bounds = in_bounds ),
            # TODO: remove magic number
            'nsteps': 1000 }

    return ret

def main(method_name, case_num, display_name):

    params = cases.index[case_num]

    retcode,t = run_method( method_name )( display = display_for_name(display_name),
                                           **( run_kwargs(params) ) )
    print((retcode,t))

def parser():
    prsr = argparse.ArgumentParser()
    prsr.add_argument( 'method',
                       help="Which method to test",
                       type=str,
                       choices=('estimate', 'navigate'),
                       default='estimate')
    prsr.add_argument( '--case',
                       help="test case number",
                       type=int,
                       default=1,
                       choices = tuple(cases.index.keys()) )
    prsr.add_argument( '--display',
                       choices=('turtle','text','none'),
                       default='turtle' )
    return prsr

if __name__ == '__main__':
    args = parser().parse_args()
    main( method_name  = args.method,
          case_num     = args.case,
          display_name = args.display )
