from builtins import object
from matrix import *
import numpy as np
import random
import math


class Pilot(object):
    measurements = []
    prev_astroids_dict = {}
    astroids_xp_dict = {}
    astroid_predictions = []
    headings = []
    time = 0
    previous_measurement = None
    x = None
    P = None

    F = np.array([
        [1., 0., 1., 0., 0., 0.],
        [0., 1., 0., 1., 0., 0.],
        [0., 0., 1., 0., 1., 0.],
        [0., 0., 0., 1., 0., 1.],
        [0., 0., 0., 0., 1., 0.],
        [0., 0., 0., 0., 0., 1.]])

    H = np.array([[1., 0., 0., 0., 0., 0.],
                  [0., 1., 0., 0., 0., 0.]])

    R = np.array([[.01, 0],
                  [0, .01]])
    # I =  np.array([[]])
    # I.identity(6)

    I = np.array([
        [1., 0., 0., 0., 0., 0.],
        [0., 1., 0., 0., 0., 0.],
        [0., 0., 1., 0., 0., 0.],
        [0., 0., 0., 1., 0., 0.],
        [0., 0., 0., 0., 1., 0.],
        [0., 0., 0., 0., 0., 1.]])

    def __init__(self, min_dist, in_bounds):
        self.min_dist = min_dist
        self.in_bounds = in_bounds

    def observe_asteroids(self, asteroid_locations):
        """ self - pointer to the current object.
           asteroid_locations - a list of asteroid observations. Each
           observation is a tuple (i,x,y) where i is the unique ID for
           an asteroid, and x,y are the x,y locations (with noise) of the
           current observation of that asteroid at this timestep.
           Only asteroids that are currently 'in-bounds' will appear
           in this list, so be sure to use the asteroid ID, and not
           the position/index within the list to identify specific
           asteroids. (The list may change in size as asteroids move
           out-of-bounds or new asteroids appear in-bounds.)

           Return Values:
                    None
        """

        self.measurements = []
        self.measurements.append(asteroid_locations)
        self.time = self.time + 1

        pass

    def next_move(self, craft_state):
        """ self - a pointer to the current object.
            craft_state - implemented as CraftState in craft.py.

            return values:
              angle change: the craft may turn left(1), right(-1),
                            or go straight (0).
                            Turns adjust the craft's heading by
                             angle_increment.
              speed change: the craft may accelerate (1), decelerate (-1), or
                            continue at its current velocity (0). Speed
                            changes adjust the craft's velocity by
                            speed_increment, maxing out at max_speed.
         """

        self.new_craft_coordinates = []

        self.max_speed = craft_state.max_speed
        self.speed_increment = craft_state.speed_increment
        self.angle_increment = craft_state.angle_increment

        self.x = craft_state.x
        self.y = craft_state.y
        self.h = craft_state.h
        self.v = craft_state.v

        self.headings.append(self.h)
        initial_heading = self.headings[0]


        self.estimate_asteroid_locs()

        self.ad = {}
        # get current and next (from Kalman Filter) positions of all astroids indexed by the astroid id
        for astroid in self.measurements[-1]:
            for new_astroid in self.astroid_predictions:
                if astroid[0] == new_astroid [0]:
                    self.ad[astroid[0]] = (astroid[1], astroid[2], new_astroid[1], new_astroid[2])

        best_options = {}

        # iterate ove all possible next choices for the craft
        for speed_change in [1, 0, -1]:
            for angle_change in [1, 0, -1]:

                # get the new coordinats based on the choice of angle and speed increments

                new_h = self.h + (angle_change * self.angle_increment)
                new_h = new_h % (2.0 * math.pi)

                new_v = self.v + (speed_change * self.speed_increment)
                new_v = min(self.max_speed, max(0.0, new_v))

                new_x = self.x + (new_v * math.cos(new_h))
                new_y = self.y + (new_v * math.sin(new_h))

                min_distance = 1000

                # iterate over all astroids currently in the system
                for i in self.ad.keys():
                    # get current and future distances between the astroid and the space craft
                    current_distance = math.sqrt((self.ad[i][0] - self.x)**2 + (self.ad[i][1] - self.y)**2)
                    next_distance = math.sqrt((self.ad[i][2] - new_x)**2 + (self.ad[i][3] - new_y)**2)
                    # check if they are getting closer to each other
                    if next_distance < current_distance:
                        # if so find the minimun distance from all current astroids w.r.t. future craft position
                        if next_distance < min_distance:
                            min_distance = next_distance

                # get the night best options, one for each choice
                best_options[(angle_change, speed_change)] = min_distance

        max_min_distance = 0

        best_h = 0
        best_v = 1

        if self.time > 6:
            # chose the option that lead to the max min distance
            for (h, v) in best_options.keys():
                if best_options[(h, v)] > max_min_distance:
                    max_min_distance = best_options[(h, v)]
                    if max_min_distance < 4 * self.v:
                        best_h = h
                        best_v = v
                    else: 
                        if(self.h != initial_heading):
                            if(self.h > initial_heading):
                                best_h = -1
                            else:
                                best_h = 1


        return best_h, best_v


    def estimate_asteroid_locs(self):
        """ Should return an itterable (list or tuple for example) that
            contains data in the format (i,x,y), consisting of estimates
            for all in-bound asteroids. """

        measurements = self.measurements
        prev_astroids_dict = self.prev_astroids_dict
        astroids_xp_dict = self.astroids_xp_dict

        returned_measurements = []
        F = self.F
        H = self.H
        R = self.R
        I = self.I

        for measurement in measurements[0]:
            if (measurement[0] in prev_astroids_dict.keys()):

                prev_astroidsSet = set(prev_astroids_dict)
                astroids_xpSet = set(astroids_xp_dict)

                for item in prev_astroidsSet.intersection(astroids_xpSet):
                    if (item == measurement[0]):
                        one_astroid = []

                        previous_astroid_mes = (prev_astroids_dict[item][0], prev_astroids_dict[item][1])
                        previous_astroid_xp = astroids_xp_dict[item][0], astroids_xp_dict[item][1]
                        current_astroid_mes = (measurement[1], measurement[2])
                        one_astroid.append(previous_astroid_mes)
                        one_astroid.append(current_astroid_mes)

                        x, P = self.kalmanFilter(previous_astroid_xp[0], previous_astroid_xp[1], one_astroid)

                        x_postion = x[0][0]
                        y_position = x[1][0]
                        returned_measurements.append((measurement[0], x_postion, y_position))

                        prev_astroids_dict.update({measurement[0]: [measurement[1], measurement[2]]})
                        astroids_xp_dict.update({measurement[0]: [x, P]})

            else:
                prev_astroids_dict.update({measurement[0]: [measurement[1], measurement[2]]})
                one_astroid = []

                x = np.array([[0.], [0.], [0.], [0.], [0.], [0.]])  # initial state (location and velocity)
                P = np.array([
                    [1., 0., 0., 0., 0., 0.],
                    [0., 1., 0., 0., 0., 0.],
                    [0., 0., 1000., 0., 0., 0.],
                    [0., 0., 0., 1000., 0., 0.],
                    [0., 0., 0., 0., 1000., 0.],
                    [0., 0., 0., 0., 0., 1000.]])

                one_astroid.append([measurement[1], measurement[2]])
                x, P = self.kalmanFilter(x, P, one_astroid)
                astroids_xp_dict.update({measurement[0]: [x, P]})

                x_postion = x[0][0]
                y_position = x[1][0]
                returned_measurements.append((measurement[0], x_postion, y_position))
                self.astroid_predictions = returned_measurements

        return returned_measurements

    def kalmanFilter(self, x, P, measurements):

        F = self.F
        H = self.H
        R = self.R
        I = self.I

        for n in range(len(measurements)):
            # measurement update
            Z = matrix([measurements[n]])
            Z = np.array([[measurements[n][0]], [measurements[n][1]]])

            y = Z - (np.dot(H, x))
            S = np.dot(H, np.dot(P, H.T)) + R
            K = np.dot(P, np.dot(H.T, np.linalg.inv(S)))
            x = x + (np.dot(K, y))
            P = np.dot((I - (np.dot(K, H))), P)

            x = np.dot(F, x)
            P = np.dot(F, np.dot(P, F.T))

        return x, P
#  python3 test_one.py --case 7 navigate