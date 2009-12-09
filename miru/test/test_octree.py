# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details
from miru.test import unittest
from miru.trees import Octree

from euclid import Vector3

class Object:
    def __init__(self, pos):
        self.pos = pos

class OctreeTest(unittest.TestCase):

    def test_partitioning(self):
        octree = Octree(width=128, min_width=16, max_population=7)
        
        for t in [(32,32,32),(32,96,32),(96,32,32),(96,96,32),
                (32,32,96),(32,96,96),(96,32,96)]:
            o = Object(Vector3(*t))
            octree.addObject(o)
            self.assertEquals(None, octree._child_nodes)
        o = Object(Vector3(96,96,96))
        octree.addObject(o)
        self.assert_(octree._child_nodes)
        
        for t in [(32,32,32),(32,96,32),(96,32,32),(96,96,32),
                (32,32,96),(32,96,96),(96,32,96),(96,96,96)]:
            node = octree.findNode(*t)
            objs = node.objects
            self.assertEquals(1, len(objs))
            for o in objs:
                self.assertEquals(t, tuple(o.pos))

        objs = octree.objects
        self.assertEquals(8, len(objs))


    def test_findNode(self):
        octree = Octree(width=128, min_width=16, max_population=7)
        # see that subdivision occurs on child nodes correctly
        for t in [(32,32,32),(32,96,32),(96,32,32),(96,96,32),
                (32,32,96),(32,96,96),(96,32,96), (96,96,96)]:
            o = Object(Vector3(*t))
            octree.addObject(o)
        node = octree.findNode(0,0,0)
        self.assertNot(node._child_nodes)
        self.assertEquals([(32,32,32)], [tuple(o.pos) for o in node.objects])
        node = octree.findNode(127,127,127)
        self.assertNot(node._child_nodes)
        self.assertEquals([(96,96,96)], [tuple(o.pos) for o in node.objects])


    
    def test_nestedParitioning(self):
        octree = Octree(width=128, min_width=16, max_population=7)
        # see that subdivision occurs on child nodes correctly
        for t in [(32,32,32),(32,96,32),(96,32,32),(96,96,32),
                  (32,32,96),(32,96,96),(96,32,96), (96,96,96),
                  (0,0,0),(1,0,0),(2,0,0),(3,0,0),(4,0,0),(5,0,0),(6,0,0)]:
            o = Object(Vector3(*t))
            octree.addObject(o)
        for t in [(35,35,35),(33,97,33),(97,33,33),(97,97,33),
                (33,33,97),(33,97,97),(97,33,97),(97,97,97)]:
            node = octree.findNode(*t)
            self.assertEquals(1, len(node.objects))
        node = octree.findNode(0,0,0)
        self.assertEquals(7, len(node.objects))
        node = octree.findNode(32,32,32)
        self.assertEquals(1, len(node.objects))

        child = octree._child_nodes[(0,0,0)]
        self.assert_(child._child_nodes)
        
        # Check that the other nodes were not partitioned
        for t in [(0,0,64),(0,64,0),(0,64,64),(64,0,0),
                  (64,0,64),(64,64,0),(64,64,64)]:
            self.assertNot(octree._child_nodes[t]._child_nodes)


    def test_secondParititioningBug(self):
        octree = Octree(width=8, min_width=2, max_population=1)
        for t in [(2,2,2),(2.5,1.5,1.5),(4.5,0,0),(5,0,0)]:
            o = Object(Vector3(*t))
            octree.addObject(o)
        node = octree._child_nodes[(4,0,0)]
        self.assertTrue(node._child_nodes.has_key((4,0,0)))
        self.assertTrue(node._child_nodes.has_key((4,2,0)))
        self.assertTrue(node._child_nodes.has_key((4,2,2)))
        self.assertTrue(node._child_nodes.has_key((4,0,2)))
        self.assertTrue(node._child_nodes.has_key((6,0,0)))
        self.assertTrue(node._child_nodes.has_key((6,2,0)))
        self.assertTrue(node._child_nodes.has_key((6,2,2)))
        self.assertTrue(node._child_nodes.has_key((6,0,2)))
        

    def test_minDivision(self):
        octree = Octree(width=4, min_width=2, max_population=7)
        for t in [(1,1,1),(1,1,3),(1,3,1),(1,3,3),
                  (3,1,1),(3,1,3),(3,3,1),(3,3,3),
                  (3.1,3,3),(3.2,3,3),(3.3,3,3),(3.4,3,3),
                  (3.5,3,3),(3.6,3,3),(3.7,3,3)]:
            o = Object(Vector3(*t))
            octree.addObject(o)
        node = octree._child_nodes[(2,2,2)]
        self.assertNot(node._child_nodes)
        node = octree.findNode(3,3,3)
        self.assertEquals(8, len(node.objects))


