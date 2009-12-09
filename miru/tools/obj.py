# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details
"""
(Limited) Import support for Wavefront obj files.

Current implementation is based on specification at:
http://www.martinreddy.net/gfx/3d/OBJ.spec

Features of the specification that are not implemented:
TODO

Features of the specification that are not well tested:
TODO
"""

from euclid import Vector3
from warnings import warn
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import os
from twisted.python import failure

from twisted.python import failure


class ObjObject(object):

    __slots__ = ['vertices', 'normals', 'material',
            'vertex_indices', 'normal_indices', 'texcoords', 'texcoord_indices']

    def __init__(self, ctx=None):
        self.vertices = []
        self.normals = []
        self.material = None
        self.texcoords = []
        self.vertex_indices = []
        self.normal_indices = []
        self.texcoord_indices = []
        # Vertices are global and shared in an OBJ file despite
        # the ordering an layout.
        if ctx:
            self.texcoords = ctx.texcoords
            self.vertices = ctx.vertices
            self.normals = ctx.normals

class ObjFace(object):

    def __init__(self):
        pass

class ObjMaterial(object):

    __slots__ = ['ambient', 'diffuse', 'specular', 'alpha', 'shininess', 'teximg_filename']

    def __init__(self):
        self.ambient = None
        self.diffuse = None
        self.specular = None
        self.alpha = None
        self.shininess = None
        self.teximg_filename = None
        
class ObjParser:

    def __init__(self, filename=None, data=None, flip_normals=False):
        self.filename = filename
        self._base = None
        if self.filename:
            self._base =  os.path.dirname(filename)
        self.data = data
        self.flip_normals = flip_normals

    def parse(self):
        """Parse data if filename given in initializer.
        This returns a dictionary of the parsed objects.
        """
        if self.data:
            fh = self.data.splitlines()
            close = lambda f : None
        else:
            fh = open(self.filename)
            close = lambda f : f.close()

        self.objects = {}
        self.current = None
        self.mat = None
        self.first = None
        self.smth_grps = {}
        self.materials = {}
        data = StringIO()

        def i_():
            n = 0
            while True:
                yield n
                n += 1

        it = i_()
        for (idx,line) in ((it.next(),l) for l in fh):
            data.write(line)
            if not line[:-1]:
                continue
            if line[0] == '#':
                continue
            tks = line.split()
            directive = tks[0]
            try:
                h = getattr(self, '_handle_%s' % directive)
                try:
                    h(tks[1:])
                except Exception, e:
                    pass
            except AttributeError:
                f = failure.Failure()
                f.printTraceback()
                #warn("Directive %s not handled" % directive)

        close(fh)
        return (self.first, self.objects, data.getvalue())

    def _handle_o(self, tks):
        # New object definition
        name = tks[0]
        self.objects[name] = self.current = ObjObject(self.current)
        if not self.first:
            self.first = self.current

    def _handle_v(self, tks):
        # Vertex
        if not self.current:
            self.current = ObjObject()
            if not self.first:
                self.first = self.current
        self.current.vertices.append(tuple([float(t) for t in tks]))

    def _handle_vn(self, tks):
        # Vertex Normal
        v = Vector3(*tuple([float(t) for t in tks]))
        v.normalize()
        # XXX it seems smoothly shaded meshes need this (at least as exported from blender)
        if self.flip_normals:
            v *= -1
        self.current.normals.append((v.x, v.y, v.z))

    def _handle_vt(self, tks):
        # XXX we assume the last number is 0.0 and we're always dealing with
        # 2D texture coords
        coords = tuple([float(n) for n in tks[:-1]])
        self.current.texcoords.append(coords)

    def _handle_s(self, tks):
        if tks[0] == 'off':
            return
        self.current.normal_indices = self.smth_grps.setdefault(tks[0], self.current.normal_indices)

    def _handle_mtllib(self, tks):
        parser = ObjMaterialParser(os.path.join(self._base, tks[0]))
        mats = parser.parse()
        self.materials.update(mats)

    def _handle_usemtl(self, tks):
        try:
            self.current.material = self.mat = self.materials[tks[0]]
        except KeyError:
            #warn('Failed looking up material : %s' % tks[0])
            pass

    def _handle_f(self, tks):
        # parse the face
        face = tks
        try:
            face[0].index('//')
            delim = '//'
        except:
            delim = '/'
        tidxs = []
        vidxs = []
        nidxs = []
        if delim == '//':
            # double slashes used when no texture indices are given
            for indices in face:
                vidx, nidx = indices.split(delim)
                vidxs.append(int(vidx)-1)
                nidxs.append(int(nidx)-1)
        else:
            for indices in face:
                vidx, tidx, nidx = indices.split(delim)
                vidxs.append(int(vidx)-1)
                nidxs.append(int(nidx)-1)
                tidxs.append(int(tidx)-1)
        if tidxs:
            self.current.texcoord_indices.append(tuple(tidxs))
        self.current.vertex_indices.append(tuple(vidxs))
        self.current.normal_indices.append(tuple(nidxs))


class ObjMaterialParser:

    def __init__(self, filename):
        self.filename = filename
        self._base = os.path.dirname(filename)

    def parse(self):
        fh = open(self.filename)

        self.materials = {}
        self.material = None

        for line in fh:
            if not line[:-1]:
                continue
            if line[0] == '#':
                continue
            tks = line.split()
            directive = tks[0]
            try:
                h = getattr(self, '_handle_%s' % directive)
                h(tks[1:])
            except AttributeError:
                #warn("[mtl] Directive `%s' not handled" % directive)
                pass
        return self.materials

    def _handle_newmtl(self, tks):
        self.materials[tks[0]] = self.material = ObjMaterial()
    
    def _handle_Ns(self, tks):
        self.material.shininess = float(tks[0])

    def _handle_Ka(self, tks):
        self.material.ambient = tuple([float(n) for n in tks])

    def _handle_Kd(self, tks):
        self.material.diffuse = tuple([float(n) for n in tks])

    def _handle_Ks(self, tks):
        self.material.specular = tuple([float(n) for n in tks])

    def _handle_d(self, tks):
        self.material.alpha = float(tks[0])

    def _handle_map_Kd(self, tks):
        self.material.teximg_filename = os.path.join(self._base, tks[0])


