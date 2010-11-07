from __future__ import division
"""
A simple interface for Bezier curves
"""

class Quadratic(object):
    def __init__(self, p0, p1, p2, tmax):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.tmax = tmax

    def B(self, t):
        """Compute the point at time t"""
        # Convert to fractional t
        t = t / self.tmax
        v =  (1-t)**2*self.p0 + 2*(1-t)*t*self.p1 + t**2*self.p2
        #print t,v
        return v
