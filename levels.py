from __future__ import division

import entity
"""
This module holds what happens for each level

"""
class Level(object):
    def __init__(self, levelnum, asteroids):
        self.levelnum = levelnum
        self.asteroids = asteroids

    def create_asteroids(self):
        """Returns a set of asteroid objects"""
        maxspeed = self.levelnum

        asteroids = set()

        for size, count in enumerate(self.asteroids):
            size += 1 # sizes start at 1
            for _ in xrange(count):
                asteroids.add( entity.Asteroid(size, maxspeed) )

        return asteroids


level = [
        Level(1, [0,0,2]),
        Level(2, [3,2,0]),
        Level(3, [5,3,1]),
        Level(4, [0,0,0,1]),
        Level(5, [0,0,2,1]),
        ]
