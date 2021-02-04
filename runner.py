
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

from builtins import range
from builtins import object
import math
import random
import copy

class BaseRunnerDisplay(object):

    def setup(self, x_bounds, y_bounds,
              in_bounds, goal_bounds,
              margin,
              noise_sigma,
              craft_max_speed,
              craft_speed_increment,
              craft_angle_increment):
        pass
    
    def begin_time_step(self, t):
        pass

    def asteroid_at_loc(self, i, x, y):
        pass

    def asteroid_estimated_at_loc(self, i, x, y, is_match=False):
        pass

    def asteroid_estimates_compared(self, num_matched, num_total):
        pass

    def craft_at_loc(self, x, y, h):
        pass

    def craft_steers(self, dh, dv):
        pass

    def collision(self):
        pass

    def out_of_bounds(self):
        pass

    def goal(self):
        pass

    def navigation_done(self, retcode, t):
        pass

    def estimation_done(self, retcode, t):
        pass
    
    def end_time_step(self, t):
        pass

    def teardown(self):
        pass

def l2( xy0, xy1 ):
    dx = xy0[0] - xy1[0]
    dy = xy0[1] - xy1[1]
    return math.sqrt( (dx * dx) + (dy * dy) )

SUCCESS = 'success'
FAILURE_TOO_MANY_STEPS = 'too_many_steps'

# Custom failure states for navigation.
NAV_FAILURE_COLLISION = 'collision'
NAV_FAILURE_OUT_OF_BOUNDS = 'out_of_bounds'

def add_observation_noise( asteroid_locations, noise_sigma=0.0,
                           random_state = None ):

    my_random_state = random_state if random_state else random.Random(0)
    ret = ()
    for i,x,y in asteroid_locations:
        err_r = my_random_state.normalvariate( mu = 0.0, sigma = noise_sigma )
        err_theta = my_random_state.random() * math.pi * 2
        err_x = err_r * math.cos( err_theta )
        err_y = err_r * math.sin( err_theta )
        ret += ((i, x + err_x, y + err_y),)
    return ret

def run_estimation( field,
                    craft_state,
                    min_dist,
                    noise_sigma,
                    in_bounds,
                    goal_bounds,
                    nsteps,
                    pilot,
                    display=None ):
    """
    TODO:  docstring
    """
    ret = (FAILURE_TOO_MANY_STEPS, nsteps)

    observation_counts = {}

    # TODO:  add parameter for seed?
    random_state = random.Random(0)
    
    display.setup( field.x_bounds, field.y_bounds,
                   in_bounds, goal_bounds,
                   margin = min_dist,
                   noise_sigma = noise_sigma,
                   craft_max_speed = craft_state.max_speed,
                   craft_speed_increment = craft_state.speed_increment,
                   craft_angle_increment = craft_state.angle_increment )

    estimated_locs = ()  # estmated locations

    for t in range(nsteps):

        display.begin_time_step(t)

        asteroid_locs = field.asteroid_locations(t)

        pilot.observe_asteroids( add_observation_noise(asteroid_locs, noise_sigma, random_state) )

        actual = {}
        matches = ()

        for i,x,y in asteroid_locs:
            display.asteroid_at_loc(i,x,y)
            actual[i] = (x,y)

        estimated_locs_seen = set()

        for i,x,y in estimated_locs:

            if i in estimated_locs_seen:
                continue

            estimated_locs_seen.add(i)

            if i in actual:
                dist = l2( (x,y), actual[i] )
                is_match = (dist < min_dist)
                if is_match:
                    matches += (i,)
            else:
                is_match = False    
            
            display.asteroid_estimated_at_loc(i,x,y,is_match)

        estimated = dict( [ (i,(x,y)) for i,x,y in estimated_locs ] )

        # Calculate estimates for next time step.
        estimated_locs = pilot.estimate_asteroid_locs()

        display.asteroid_estimates_compared( len(matches), len(actual) )

        # If this step's estimates were good enough, we're done.
        if len(matches) > len(actual) * 0.9:  # TODO:  fix magic number
            ret = (SUCCESS, t)
            display.end_time_step(t)
            break
        else:
            display.end_time_step(t)

    display.estimation_done( *ret )
    display.teardown()
    return ret

def run_navigation( field,
                    craft_state,
                    min_dist,
                    noise_sigma,
                    in_bounds,
                    goal_bounds,
                    nsteps,
                    pilot,
                    display=None ):

    """
    TODO:  docstring
    """

    ret = (FAILURE_TOO_MANY_STEPS, nsteps)
    random_state = random.Random(0)

    display.setup( field.x_bounds, field.y_bounds,
                   in_bounds, goal_bounds,
                   margin = min_dist,
                   noise_sigma = noise_sigma,
                   craft_max_speed = craft_state.max_speed,
                   craft_speed_increment = craft_state.speed_increment,
                   craft_angle_increment = craft_state.angle_increment )

    for t in range(nsteps):

        display.begin_time_step(t)

        cx,cy,ch = craft_state.position
        display.craft_at_loc( cx, cy, ch )

        astlocs = field.asteroid_locations(t)

        pilot.observe_asteroids( add_observation_noise(astlocs, noise_sigma, random_state) )

        collisions = ()
            
        for i,x,y in astlocs:
            display.asteroid_at_loc(i,x,y)
            if l2( (cx,cy), (x,y) ) < min_dist:
                collisions += (i,)

        if collisions:
            ret = (NAV_FAILURE_COLLISION, t)
            display.navigation_done(*ret)
            display.end_time_step(t)
            break

        elif goal_bounds.contains( (cx,cy) ):
            ret = (SUCCESS, t)
            display.navigation_done(*ret)
            display.end_time_step(t)
            break

        elif not in_bounds.contains( (cx,cy) ):
            ret = (NAV_FAILURE_OUT_OF_BOUNDS, t)
            display.navigation_done(*ret)
            display.end_time_step(t)
            break

        else:
            # notify pilot of measurements
            dh,dv = pilot.next_move( craft_state = copy.deepcopy(craft_state) )
            craft_state = craft_state.steer( dh, dv )
            display.craft_steers( dh, dv )
            display.end_time_step(t)

    display.teardown()
    return ret
