# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details
from miru.test import unittest
from miru import track
from miru.camera import Camera
from miru.core import Object

class TrackTest(unittest.TestCase):


    def test_tracked_independence(self):
        tracker = Object()
        tracked = Object()

        trk = track.PosTrack(tracker, tracked)
        self.assertEquals((0,0,0), tuple(tracked.pos))

        tracker.pos = (1,2,3)
        self.assertEquals((0,0,0), tuple(tracked.pos))
        self.assertEquals((1,2,3), tuple(tracker.pos))


    def test_tracker_dependence(self):
        tracker = Object(pos=(3,4,5))
        self.assertEquals((3,4,5), tuple(tracker.pos))
        tracked = Object()

        trk = track.PosTrack(tracker, tracked)
        tracked.pos = (1,4,6)

        self.assertEquals((1,4,6), tuple(tracked.pos))
        self.assertEquals((4,8,11), tuple(tracker.pos))

        tracked.pos += (2,-3,1)

        self.assertEquals((3,1,7), tuple(tracked.pos))
        self.assertEquals((6,5,12), tuple(tracker.pos))

        tracked.pos += (0,0,0)

        self.assertEquals((3,1,7), tuple(tracked.pos))
        self.assertEquals((6,5,12), tuple(tracker.pos))

    def test_axis_tracking(self):

        tracker = Object()
        tracked = Object()
        trk = track.PosTrack(tracker, tracked, axes=(1,0,0))
        tracked.pos += (1,2,3)
        self.assertEquals((1,2,3), tuple(tracked.pos))
        self.assertEquals((1,0,0), tuple(tracker.pos))
        
        tracker = Object()
        tracked = Object()
        trk = track.PosTrack(tracker, tracked, axes=(0,1,0))
        tracked.pos += (1,2,3)
        self.assertEquals((1,2,3), tuple(tracked.pos))
        self.assertEquals((0,2,0), tuple(tracker.pos))

        tracker = Object()
        tracked = Object()
        trk = track.PosTrack(tracker, tracked, axes=(0,0,1))
        tracked.pos += (1,2,3)
        self.assertEquals((1,2,3), tuple(tracked.pos))
        self.assertEquals((0,0,3), tuple(tracker.pos))
        
        tracker = Object()
        tracked = Object()
        trk = track.PosTrack(tracker, tracked, axes=(1,0,1))
        tracked.pos += (1,2,3)
        self.assertEquals((1,2,3), tuple(tracked.pos))
        self.assertEquals((1,0,3), tuple(tracker.pos))



    def test_deactivation(self):
        tracker = Object(pos=(3,4,5))
        tracked = Object()

        trk = track.PosTrack(tracker, tracked)
        trk.deactivate()
        tracked.pos = (1,4,6)

        self.assertEquals((1,4,6), tuple(tracked.pos))
        self.assertEquals((3,4,5), tuple(tracker.pos))


    def test_tracker_registry(self):
        tracker = Object()
        tracked = Object()

        trk = track.PosTrack(tracker, tracked)

        self.assertEquals([trk], track.gettracks(tracker=tracker))
        self.assertEquals([trk], track.gettracks(tracked=tracked))

        # no collision - duh
        trk2 = track.PosTrack(Object(), Object())
        self.assertEquals([trk], track.gettracks(tracker=tracker))
        self.assertEquals([trk], track.gettracks(tracked=tracked))

        # add a new track with tracker track

        trk3 = track.PosTrack(tracker, Object())
        self.assertEquals([trk, trk3], track.gettracks(tracker=tracker))

        # Find a track by the (tracker, tracked) tuple
        self.assertEquals([trk], track.gettracks(track=(tracker,tracked)))


    def test_global_deactivation(self):
        tracker = Object()
        tracker2 = Object()
        tracked = Object()
        track.PosTrack(tracker, tracked)
        track.PosTrack(tracker2, tracked)
        
        # Deactivate by the tracker
        track.deactivate(tracker=tracker)

        tracked.pos = (1,1,1)
        self.assertEquals((0,0,0), tracker.pos)
        self.assertEquals((1,1,1), tracker2.pos)

        track.deactivate(tracker=tracker2)

        tracked.pos += (1,2,3)
        self.assertEquals((1,1,1), tracker2.pos)

        # Recreate the tracks
        track.PosTrack(tracker, tracked)
        track.PosTrack(tracker2, tracked)
        tracked.pos += (1,2,3)

        # Deactivate by the tracked
        track.deactivate(tracked=tracked)
        tracked.pos += (4,5,6)
        self.assertEquals((1,2,3), tracker.pos)
        self.assertEquals((2,3,4), tracker2.pos)


    def test_mutualTracks(self):
        # Check for not infinite recursion
        o1 = Object()
        o2 = Object()
        trk1 = track.PosTrack(o1, o2)
        trk2 = track.PosTrack(o2, o1)

        o1.pos += (1,0,0)

        self.assertEquals((1,0,0), o2.pos)

        o2.pos += (0,1,0)

        self.assertEquals((1,1,0), o1.pos)

