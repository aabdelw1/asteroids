
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

from builtins import object
class BoundsRectangle(object):

    def __init__(self, x_bounds, y_bounds):
        self.x_bounds = x_bounds
        self.y_bounds = y_bounds

    def contains(self, xy):
        return ((self.x_bounds[0] <= xy[0] <= self.x_bounds[1])
                and (self.y_bounds[0] <= xy[1] <= self.y_bounds[1]))
