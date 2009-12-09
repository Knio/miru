import math
import euclid
import pyglet.gl as gl
import pyglet.graphics
import pyglet

# Geometry for testing in applications


def _flatten(l):
    nl = []
    for i in l:
        nl.extend(i)
    return nl

def _rotated_z(v, angle):
    if not angle:
        return v

    sin_angle = math.sin(math.pi * angle/180)
    cos_angle = math.cos(math.pi * angle/180)
    
    return euclid.Vector3(
        v.x*cos_angle - v.y*sin_angle,
        v.x*sin_angle + v.y*cos_angle,
        v.z)

def _rotated_y(v, angle):
    if not angle:
        return v

    sin_angle = math.sin(math.pi * angle/180)
    cos_angle = math.cos(math.pi * angle/180)
    
    return euclid.Vector3(
        v.x*cos_angle + v.z*sin_angle,
        v.y,
        -v.x*sin_angle + v.z*cos_angle)


class Torus(object):

    _cache = {}
    drawing_mode = gl.GL_TRIANGLES
    vertex_pitch = 3

    def __init__(self, divisions=132, inner_radius=0.5, outer_radius=1.5):
        k = (divisions, inner_radius, outer_radius)
        torus = self._cache.get(k, None)
        if not torus:
            self._build(divisions, inner_radius, outer_radius)
            self._cache[k] = self
        else:
            self.vertex_count = torus.vertex_count
            self.vertices = self.vertex_data = list(torus.vertices)
            self.normals = self.normal_data = list(torus.normals)
            self.indices = list(torus.indices)

    def _build(self, divisions, inner_radius, outer_radius):
        

        self.vertex_count = vcount = (divisions + 1) * (divisions + 1)

        # Fill out the arrays to avoid index errors
        self.vertices = self.vertex_data = vertices = [0.0] * (vcount * 3)
        self.normals = self.normal_data = normals = [0.0] * (vcount * 3)
        self.indices = indices = [0.0] * (2 * divisions * divisions * 3)


        for i in xrange(divisions+1):
            angle = i * 360. / divisions

            pos = (_rotated_z( euclid.Vector3(inner_radius, 0.0, 0.0), angle ) +
                    euclid.Vector3(outer_radius, 0., 0.))
            vertices[i*3:i*3+3] = (pos.x, pos.y, pos.z)

            sTangent = euclid.Vector3(0.0, 0.0, -1.0)
            tTangent = _rotated_z(euclid.Vector3(0., -1., 0.), i*360./divisions)
            normal = tTangent.cross(sTangent)
            normals[i*3:i*3+3] = (normal.x, normal.y, normal.z)

        for ring in xrange(divisions+1):
            for i in xrange(divisions+1):

                angle = ring * 360. / divisions
                idx = (ring*(divisions+1)+i) * 3
                vertex = self.vertices[idx]
                v = _rotated_y(euclid.Vector3(*vertices[i*3:i*3+3]), angle)
                vertices[idx:idx+3] = [v.x, v.y, v.z]

                v = _rotated_y(euclid.Vector3(*normals[i*3:i*3+3]), angle)
                normals[idx:idx+3] = [v.x, v.y, v.z]

        for ring in range(divisions):
            for i in range(divisions):
                indices[ ((ring*divisions+i)*2)*3+0  ] = ring * (divisions + 1) + i
                indices[ ((ring*divisions+i)*2)*3+1  ] = (ring + 1) * (divisions + 1) + i
                indices[ ((ring*divisions+i)*2)*3+2  ] = ring * (divisions + 1) + i + 1
                indices[ ((ring*divisions+i)*2+1)*3+0] = ring * (divisions + 1) + i + 1
                indices[ ((ring*divisions+i)*2+1)*3+1] = (ring + 1) * (divisions + 1) + i
                indices[ ((ring*divisions+i)*2+1)*3+2] = (ring + 1) * (divisions + 1) + i + 1


def get_vlist(geom, batch=None, group=None, data=None):
        """Get a "new" C{pyglet.graphics.VertexList} for this
        geometry.  If a batch is given, vertex list will be added to the batch
        """
        # projection with one world coordinate unit equal to one screen pixel
        # glMatrixMode (GL_PROJECTION); glLoadIdentity (); gluOrtho2D (0, windowWidth, 0, windowHeight);
        window = pyglet.window.get_platform().get_default_display().get_windows()[0]
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluOrtho2D(0,
                      window.width,
                      0,
                      window.height)
        _data = [('v3f', geom.vertex_data)]
        if hasattr(geom, 'normal_data'):
            _data.append(('n3f', geom.normal_data))
        if hasattr(geom, 'texcoord_data'):
            _data.append(('t2f', geom.texcoord_data))
        if data:
            _data.extend(data)
        count = len(geom.vertex_data) // geom.vertex_pitch
        indexed = hasattr(geom, 'indices')
        if batch:
            if indexed:
                return batch.add_indexed( count,
                        geom.drawing_mode, group, geom.indices, *_data)
            return batch.add( count,
                    geom.drawing_mode, group, *_data)
        if indexed:
            return pyglet.graphics.vertex_list_indexed( count, geom.indices, *_data )
        return pyglet.graphics.vertex_list( count, *_data)


def transform(geom, translation=None):
    vertices = geom.vertex_data
    for idx in range(0, len(vertices), geom.vertex_pitch):
        vertices[idx:idx+3] = (
                vertices[idx] + translation[0],
                vertices[idx+1] + translation[1],
                vertices[idx+2] + translation[2])


class Box(object):

    indexed = False
    vertex_pitch = 3
    drawing_mode = gl.GL_QUADS

    def __init__(self, width=5):
        cube = Cube(width)
        self.vertex_data = cube.vertex_data#cube.vertex_data[:-12]
        # reverse drawing order
        for idx in range(0, len(self.vertex_data), 12):
            v = self.vertex_data[idx:idx+12]
            self.vertex_data[idx:idx+12] = (
                v[9], v[10], v[11],
                v[6], v[7], v[8],
                v[3], v[4], v[5],
                v[0], v[1], v[2]
            )
        self.normal_data = cube.normal_data#cube.normal_data[:-12]
        # flip normals
        for idx in range(0, len(self.normal_data), 3):
            s = self.normal_data[idx:idx+3]
            self.normal_data[idx:idx+3] = (-1 * s[0], -1 * s[1], -1 * s[2])

            
class Rectangle (object):
    indexed = False
    vertex_pitch = 3
    drawing_mode = gl.GL_QUADS

    def __init__(self, width=16, height=9, depth=5, tex=None):
        w = width * 0.5
        h = height * 0.5
        z = depth * 0.5
        fbl = (-w, -h, z)
        ftl = (-w, h, z)
        btl = (-w, h, -z)
        bbl = (-w, -h, -z)
        
        bbr = (w, -h, -z)
        btr = (w, h, -z)
        ftr = (w, h, z)
        fbr = (w, -h, z)
        
        self.vertex_data = _flatten([
            ftl, fbl, fbr, ftr
        ])
        self.normal_data = [
            0,0,1, 0,0,1, 0,0,1, 0,0,1]
        if tex:
            self.texcoord_data = [
                0, tex.height,
                0, 0,
                tex.width, 0,
                tex.width, tex.height,
                ]
        else:
            self.texcoord_data = [
                0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0 ]
        
        
class Cube(object):
    indexed = False
    vertex_pitch = 3
    drawing_mode = gl.GL_QUADS

    def __init__(self, width=2):
        w = width * 0.5
        fbl = (-w, -w, w)
        ftl = (-w, w, w)
        btl = (-w, w, -w)
        bbl = (-w, -w, -w)
        
        bbr = (w, -w, -w)
        btr = (w, w, -w)
        ftr = (w, w, w)
        fbr = (w, -w, w)
        self.vertex_data = _flatten([
            fbl, ftl, btl, bbl, # left side
            bbl, btl, btr, bbr, # back 
            bbr, btr, ftr, fbr, # right side
            btl, ftl, ftr, btr, # top
            fbl, bbl, bbr, fbr, # bottom
            ftl, fbl, fbr, ftr # front
        ])
        self.normal_data = [
            -1,0,0,   -1,0,0,  -1,0,0,  -1,0,0,
            0,0,-1,   0,0,-1,  0,0,-1,  0,0,-1,
            1,0,0, 1,0,0, 1,0,0, 1,0,0,
            0,1,0, 0,1,0,  0,1,0,  0,1,0,
            0,-1,0,  0,-1,0,  0,-1,0, 0,-1,0,
            0,0,1, 0,0,1, 0,0,1, 0,0,1]
        self.texcoord_data = [
            1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0,    #left
            1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0,    #back
            1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0,    #right
            0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0,    #top
            0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0,    #bottom
            0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0 ]   #front



class Sphere(object):

    drawing_mode = gl.GL_TRIANGLES
    vertex_pitch = 3
    _cache = {}

    def __init__(self, radius=1.0, slices=32, stacks=32):
        k = (radius, slices, stacks)
        if not Sphere._cache.has_key(k):
            self._build(radius, slices, stacks)
        else:
            cached = Sphere._cache[k]
            self.vertex_data = list(cached.vertex_data)
            self.normal_data = list(cached.normal_data)
            self.texcoord_data = list(cached.texcoord_data)

    def _build(self, radius, slices, stacks):
        drho = math.pi / stacks
        dtheta = 2.0 * math.pi / slices
        ds = 1.0 / slices
        dt = 1.0 / stacks
        t = 1.0
        s = 0.0
        self.vertex_data = []
        self.normal_data = []
        self.texcoord_data = []
        
        for i in range(stacks):
            rho = i * drho
            srho = math.sin(rho)
            crho = math.cos(rho)
            srhodrho = math.sin(rho + drho)
            crhodrho = math.cos(rho + drho)
            
            strip_vertices = []
            strip_normals = []
            strip_texcoords = []
            s = 0.0
            for j in range(slices + 2):
                if j == slices:
                    theta = 0.0
                else:
                    theta = j * dtheta
                stheta = -math.sin(theta)
                ctheta = -math.cos(theta)
                
                x = stheta * srho
                y = ctheta * srho
                z = crho

                if len(strip_vertices) > 2:# and j % 2:
                    for (v0, v1, v2) in [(-4, -3, -2),(-2,-3,-1)]:
                        self.vertex_data.extend(strip_vertices[v2])
                        self.vertex_data.extend(strip_vertices[v1])
                        self.vertex_data.extend(strip_vertices[v0])
                        self.normal_data.extend(strip_normals[v2])
                        self.normal_data.extend(strip_normals[v1])
                        self.normal_data.extend(strip_normals[v0])
                        self.texcoord_data.extend(strip_texcoords[v2])
                        self.texcoord_data.extend(strip_texcoords[v1])
                        self.texcoord_data.extend(strip_texcoords[v0])

                
                strip_texcoords.append((s,t))
                strip_normals.append((x, y, z))
                strip_vertices.append((x * radius, y * radius, z * radius))
                
                x = stheta * srhodrho
                y = ctheta * srhodrho
                z = crhodrho
                strip_texcoords.append((s, t - dt))
                s += ds
                strip_normals.append((x, y, z))
                strip_vertices.append((x * radius, y * radius, z * radius))


            t -= dt
