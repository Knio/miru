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

from warnings import warn
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import os

class ObjObject(object):

    __slots__ = [
        'vertices', 
        'normals', 
        'material',
        'vertex_indices',
        'normal_indices', 
        'texcoords', 
        'texcoord_indices',
        'faces',
    ]

    def __init__(self, ctx=None):
        self.vertices = []
        self.normals = []
        self.material = None
        self.texcoords = []
        self.vertex_indices = []
        self.normal_indices = []
        self.texcoord_indices = []
        self.faces = []
        # Vertices are global and shared in an OBJ file despite
        # the ordering an layout.
        if ctx:
            self.texcoords = ctx.texcoords
            self.vertices = ctx.vertices
            self.normals = ctx.normals

class ObjFace(object):
    __slots__ = [
        'size',
        'material',
        'vertices',
        'textures',
        'normals',
    ]
    def __init__(self):
        pass

class ObjMaterial(object):

    __slots__ = [
        'ambient', 
        'diffuse', 
        'specular', 
        'alpha', 
        'shininess', 
        'teximg_filename'
    ]

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
            if not line.strip():
                continue
            if line.strip()[0] == '#':
                continue
            tks = line.split()
            directive = tks[0]
            try:
                h = getattr(self, '_handle_%s' % directive)
                h(tks[1:])
            except Exception, e:
                print "Error parsing line %d:" % idx
                print line
                raise
            
        close(fh)
        return (self.first, self.objects, data.getvalue())

    def _handle_g(self, tks):
        #self.current.groups = tks
        pass

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
            self.first = self.first or self.current
        self.current.vertices.append(tuple(map(float, tks)))

    def _handle_vn(self, tks):
        # Vertex Normal
        x,y,z = tuple([float(t) for t in tks])
        if self.flip_normals:
            x, y, z = -x, -y, -z
        self.current.normals.append((x, y, z))

    def _handle_vt(self, tks):
        coords = tuple(map(float, tks))
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
            print 'Warning: material %s not found' % tks[0]
        
    def _handle_f(self, face):
        # parse the face
        vidxs = []
        tidxs = []
        nidxs = []
        
        for indices in face:
            tk = indices.split('/')
            v = int(tk[0])
            t = len(tk) >= 2 and tk[1] and int(tk[1]) or 0
            n = len(tk) >= 3 and tk[1] and int(tk[1]) or 0
            if v < 0: v = len(self.current.vertices)  + v + 1
            if t < 0: t = len(self.current.texcoords) + t + 1
            if n < 0: n = len(self.current.normals)   + n + 1
            vidxs.append(v)
            tidxs.append(t)
            nidxs.append(n)
        
        face = ObjFace()
        face.size = len(vidxs)
        face.vertices = tuple(self.current.vertices [i-1] for i in vidxs)
        face.textures = tuple(i and self.current.texcoords[i-1] or None for i in tidxs)
        face.normals  = tuple(i and self.current.normals  [i-1] or None for i in nidxs)
        face.material = self.current.material
        
        self.current.faces.append(face)
        
        self.current.vertex_indices.  append(tuple(vidxs))
        self.current.texcoord_indices.append(tuple(tidxs))
        self.current.normal_indices.  append(tuple(nidxs))


class ObjMaterialParser:

    def __init__(self, filename):
        self.filename = filename
        self._base = os.path.dirname(filename)

    def parse(self):
        fh = open(self.filename)

        self.materials = {}
        self.material = None

        for line in fh:
            if not line.strip():
                continue
            if line.strip()[0] == '#':
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


