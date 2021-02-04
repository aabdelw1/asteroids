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

import sys

from runner import BaseRunnerDisplay

class TextRunnerDisplay(BaseRunnerDisplay):

    def __init__(self, fout=None):
        self.fout = fout
    
    def _log(self, s):
        fout = self.fout or sys.stdout
        if hasattr(self, 't'):
            fout.write( "[t %d]  %s\n" % (self.t, s) )
        else:
            fout.write( "%s\n" % s )

    def setup(self, x_bounds, y_bounds,
              in_bounds, goal_bounds,
              margin,
              noise_sigma,
              craft_max_speed,
              craft_speed_increment,
              craft_angle_increment):
        self._log("setup  margin: %f  noise_sigma: %f  craft_max_speed: %f  craft_speed_increment: %f  craft_angle_increment: %f"
                  % (margin, noise_sigma, craft_max_speed, craft_speed_increment, craft_angle_increment))
        self.t = 0
    
    def begin_time_step(self, t):
        self.t = t

    def asteroid_at_loc(self, i, x, y):
        pass

    def asteroid_estimated_at_loc(self, i, x, y, is_match=False):
        pass

    def asteroid_estimates_compared(self, num_matched, num_total):
        self._log("estimates matching: %d / %d"
                  % (num_matched, num_total))
        pass

    def craft_at_loc(self, x, y, h):
        self._log("craft position: (%f, %f, %f)"
                  % (x, y, h) )

    def craft_steers(self, dh, dv):
        self._log("craft steers %d, %d"
                  % (dh, dv) )
    
    def navigation_done(self, retcode, t):
        self._log("navigation done:  %s" % retcode)

    def estimation_done(self, retcode, t):
        self._log("estimation done:  %s" % retcode)

    def end_time_step(self, t):
        pass

    def teardown(self):
        pass

