
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
import random

class Asteroid(object):

    def __init__(self,
                 a_x, b_x, c_x,
                 a_y, b_y, c_y, t_start):
        self.a_x = a_x
        self.b_x = b_x
        self.c_x = c_x
        self.a_y = a_y
        self.b_y = b_y
        self.c_y = c_y
        self.t_start = t_start

    @property
    def params(self):
        return { 'a_x':     self.a_x,
                 'b_x':     self.b_x,
                 'c_x':     self.c_x,
                 'a_y':     self.a_y,
                 'b_y':     self.b_y,
                 'c_y':     self.c_y,
                 't_start': self.t_start }

    def x(self, t):

        t_shifted = t - self.t_start
        
        x = ((self.a_x * t_shifted * t_shifted)
             + (self.b_x * t_shifted)
             + self.c_x)

        return x

    def y(self, t):

        t_shifted = t - self.t_start
        
        y = ((self.a_y * t_shifted * t_shifted)
             + (self.b_y * t_shifted)
             + self.c_y)

        return y

FIELD_X_BOUNDS = (-1.0, 1.0)
FIELD_Y_BOUNDS = (-1.0, 1.0)

class AsteroidField(object):
    
    def __init__(self,
                 asteroids,
                 x_bounds = FIELD_X_BOUNDS,
                 y_bounds = FIELD_Y_BOUNDS):

        self.asteroids = asteroids
        self.x_bounds = x_bounds
        self.y_bounds = y_bounds

    def asteroid_locations(self, t):

        """
        Returns (i, x, y) tuples indicating that the i-th asteroid is
        at location (x,y).
        """
        
        locs =  [ (i, a.x(t), a.y(t))
                  for i,a in enumerate(self.asteroids)
                  if a.t_start <= t ]

        return [ (i,x,y) for i,x,y in locs
                 if self.x_bounds[0] <= x <= self.x_bounds[1]
                 and self.y_bounds[0] <= y <= self.y_bounds[1] ]

