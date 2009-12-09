# -*- test-case-name: miru.test.test_octree -*-
# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details

# Octree implementation

from pyglet import gl

from miru import imiru

import euclid
from math import floor

from zope.interface import implements

# TODO - give each node in an octree immediate access to its neighbors
# or provide a method findNodes(x,y,z) which returns something like:
# (node, {(0,0,-1):behindNode,(0,0,1):inFrontNode,(0,1,0):None ..}

class Octree(object):

    def __init__(self, max_population=25, corner=None, width=0x10000, min_width=0x80, top=None):
        self._child_nodes = None
        self._objects = []
        self.max_population = max_population
        self.corner = corner or euclid.Vector3(0,0,0)
        self.width = width
        self.min_width = min_width
        self.top = top or self
        self._objs_cache = None

    def addObject(self, obj):
        self._objs_cache = None
        if not self._child_nodes:
            self._objects.append(obj)
            if len(self._objects) > self.max_population:
                # subdivide the current octree in 8 children
                # and move objects there
                w = int(self.width / 2)
                # TODO decide the apropriate behavior if we have too many objects
                # in a region, but the region cannot be subdivied anymore.
                # raise an exception?
                if w >= self.min_width:
                    self._child_nodes = {}
                    x, y, z = tuple(self.corner)
                    for t in [(x,y,z), (x+w,y,z), (x,w+y,z),(w+x,w+y,z),
                            (x,y,w+z), (w+x,y,w+z), (x,w+y,w+z), (w+x,w+y,w+z)]:
                            v = euclid.Vector3(*t)
                            child = Octree(max_population=self.max_population,
                                    corner=v, width=w,
                                    min_width=self.min_width,
                                    top=self.top)
                            self._child_nodes[tuple(v)] = child
                    for o in self.objects:
                        (x, y, z) = self._index(o.pos.x, o.pos.y, o.pos.z)
                        node = self._child_nodes[(x,y,z)]
                        node.addObject(o)
                    self._objects = None
            return
        (x,y,z) = self._index(obj.pos.x, obj.pos.y, obj.pos.z)
        node = self._child_nodes[(x,y,z)]
        node.addObject(obj)
        
    def findNode(self, x, y, z):
        if not self._child_nodes:
            return self
        node = self._child_nodes[self._index(x,y,z)]
        return node.findNode(x, y, z)

    def _index(self, x, y, z):
        w = self.width / 2
        return (int(floor(x / w) * w), int(floor(y / w) * w), int(floor(z / w) * w))

    def _accumulate(self, objects):
        if self._objects is not None:
            objects.extend(self._objects)
        else:
            for child in self._child_nodes.values():
                child._accumulate(objects)

    @property
    def objects(self):
        if self._objs_cache:
            return self._objs_cache
        objects = []
        self._accumulate(objects)
        self._objs_cache = objects
        return objects


class OctreeDebug:
    implements(imiru.IDebuggingDrawable)
    renderStages = (imiru.IDebuggingRenderStage,)

    def __init__(self, octree, color=(0,0,1)):
        self.octree = octree
        self.color = color
        self.list_id = None
        self._cache = {}

    def draw(self):
        self._draw()

    def _draw(self):
        corner = c = self.octree.corner
        w = self.octree.width

        gl.glPushAttrib( gl.GL_ENABLE_BIT )
        gl.glEnable( gl.GL_COLOR_MATERIAL )

        if self.octree._child_nodes is None:
            if self.list_id:
                gl.glCallList(self.list_id)
            else:
                self.list_id = gl.glGenLists(1)
                gl.glNewList(self.list_id, gl.GL_COMPILE)

                gl.glColor3f(*self.color)
                gl.glBegin(gl.GL_LINE_LOOP)
                gl.glVertex3f(*c)
                gl.glVertex3f(*(c + (0,w,0)))
                gl.glVertex3f(*(c + (0,w,w)))
                gl.glVertex3f(*(c + (0,0,w)))
                gl.glEnd()

                c = corner + (w,0,0)

                gl.glBegin(gl.GL_LINE_LOOP)
                gl.glVertex3f(*c)
                gl.glVertex3f(*(c + (0,w,0)))
                gl.glVertex3f(*(c + (0,w,w)))
                gl.glVertex3f(*(c + (0,0,w)))
                gl.glEnd()

                gl.glBegin(gl.GL_LINES)
                gl.glVertex3f(*c)
                gl.glVertex3f(*(c - (w,0,0)))
                gl.glVertex3f(*(c + (0,w,0)))
                gl.glVertex3f(*(corner + (0,w,0)))
                gl.glVertex3f(*(c + (0,w,w)))
                gl.glVertex3f(*(corner + (0,w,w)))
                gl.glVertex3f(*(c + (0,0,w)))
                gl.glVertex3f(*(corner + (0,0,w)))
                gl.glEnd()

                gl.glEndList()

        # This could be optimized of course
        if self.octree._child_nodes is not None:
            r = self.color[0] + 0.14
            if r < 1.0:
                r = r % 1.0
            else:
                r = 1.0
            b = max((self.color[2] - 0.14), 0)
            for node in self.octree._child_nodes.values():
                if not self._cache.has_key(id(node)):
                    self._cache[id(node)] = OctreeDebug(node, color=(r,0,b))
                debugNode = self._cache[id(node)]
                debugNode._draw()
        gl.glColor3f(1,1,1)

        gl.glPopAttrib()
