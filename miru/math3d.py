#
# Most of this code was lifted from R. Wright's math3d library
# used in examples for OpenGL Super Bible

from pyglet.gl import *

from euclid import Vector3

import ctypes
import math

EPSILON = 0.000001

def project_xy(obj=None, pos=None):
    """Return screen coordinate or object as an (x,y) tuple.

    @param pos: The position
    
    @param obj: The object
    """
    if obj:
        pos = obj.pos

    modelView = (GLfloat * 16)()
    projection = (GLfloat * 16)()
    viewPort = (GLint * 4)()
    glGetFloatv(GL_MODELVIEW_MATRIX, modelView)
    glGetFloatv(GL_PROJECTION_MATRIX, projection)
    glGetIntegerv(GL_VIEWPORT, viewPort)

    forth = (GLfloat * 4)()
    back = (GLfloat * 4)()
    back[:3] = tuple(pos)
    back[3] = 1.0

    forth = _transformVector4(back, modelView)
    back = _transformVector4(forth, projection)

    if not _close(back[3], 0):
        d = 1.0 / back[3]
        back[0] *= d
        back[1] *= d
        back[2] *= d

    result = (back[0] * 0.5 + 0.5, back[1] * 0.5 + 0.5)
    return (result[0] * viewPort[2] + viewPort[0],
            result[1] * viewPort[3] + viewPort[1])

projectXY = project_xy

def _close(n1, n2):
    return abs(n1 - n2) <= EPSILON

# deprecated
def _transformVector4(v, m):
    tv = (GLfloat * 4)()
    tv[0] = m[0] * v[0] + m[4] * v[1] + m[8] *  v[2] + m[12] * v[3]
    tv[1] = m[1] * v[0] + m[5] * v[1] + m[9] *  v[2] + m[13] * v[3]
    tv[2] = m[2] * v[0] + m[6] * v[1] + m[10] * v[2] + m[14] * v[3]
    tv[3] = m[3] * v[0] + m[7] * v[1] + m[11] * v[2] + m[15] * v[3]
    return tv

def degrees_to_radians(d):
    return d * math.pi / 180.

radians = degrees_to_radians

def radians_to_degrees(r):
    return r * 180. / math.pi

degrees = radians_to_degrees

def c_invert_matrix4(dst, src):

    mat = lambda m,r,c : m[c*4+r]
    rc = lambda r,c: c*4+r
    def swap_rows(a, b):
        tmp = a[:8]
        a[:8] = b[:8]
        b[:8] = tmp[:]

    #float wtmp[4][8]
    #float m0, m1, m2, m3, s
    #float *r0, *r1, *r2, *r3

    #r0 = wtmp[0], r1 = wtmp[1]; r2 = wtmp[2], r3 = wtmp[3]
    r0 = (ctypes.c_float * 8)()
    r1 = (ctypes.c_float * 8)()
    r2 = (ctypes.c_float * 8)()
    r3 = (ctypes.c_float * 8)()

    r0[0] = mat(src,0,0); r0[1] = mat(src,0,1)
    r0[2] = mat(src,0,2); r0[3] = mat(src,0,3)
    r0[4] = 1.0; r0[5] = r0[6] = r0[7] = 0.0

    r1[0] = mat(src,1,0); r1[1] = mat(src,1,1)
    r1[2] = mat(src,1,2); r1[3] = mat(src,1,3)
    r1[5] = 1.0; r1[4] = r1[6] = r1[7] = 0.0

    r2[0] = mat(src,2,0); r2[1] = mat(src,2,1)
    r2[2] = mat(src,2,2); r2[3] = mat(src,2,3)
    r2[6] = 1.0; r2[4] = r2[5] = r2[7] = 0.0

    r3[0] = mat(src,3,0); r3[1] = mat(src,3,1)
    r3[2] = mat(src,3,2); r3[3] = mat(src,3,3)
    r3[7] = 1.0; r3[4] = r3[5] = r3[6] = 0.0

    # choose pivot - or die
    if abs(r3[0]) > abs(r2[0]):
        swap_rows(r3, r2)
    if abs(r2[0]) > abs(r1[0]):
        swap_rows(r2, r1)
    if abs(r1[0]) > abs(r0[0]):
        swap_rows(r1, r0)
    if 0.0 == r0[0]:
        return False

    # eliminate first variable 
    m1 = r1[0]/r0[0]; m2 = r2[0]/r0[0]; m3 = r3[0]/r0[0]
    s = r0[1]; r1[1] -= m1 * s; r2[1] -= m2 * s; r3[1] -= m3 * s
    s = r0[2]; r1[2] -= m1 * s; r2[2] -= m2 * s; r3[2] -= m3 * s
    s = r0[3]; r1[3] -= m1 * s; r2[3] -= m2 * s; r3[3] -= m3 * s
    s = r0[4]
    if (s != 0.0):
        r1[4] -= m1 * s; r2[4] -= m2 * s; r3[4] -= m3 * s
    s = r0[5]
    if (s != 0.0):
        r1[5] -= m1 * s; r2[5] -= m2 * s; r3[5] -= m3 * s
    s = r0[6]
    if (s != 0.0):
        r1[6] -= m1 * s; r2[6] -= m2 * s; r3[6] -= m3 * s
    s = r0[7]
    if (s != 0.0):
        r1[7] -= m1 * s; r2[7] -= m2 * s; r3[7] -= m3 * s

    # choose pivot - or die
    if (abs(r3[1]) > abs(r2[1])):
        swap_rows(r3, r2)
    if (abs(r2[1]) > abs(r1[1])):
        swap_rows(r2, r1)
    if 0.0 == r1[1]:
        return False

    # eliminate second variable
    m2 = r2[1]/float(r1[1]); m3 = r3[1]/float(r1[1])
    r2[2] -= m2 * r1[2]; r3[2] -= m3 * r1[2]
    r2[3] -= m2 * r1[3]; r3[3] -= m3 * r1[3]
    s = r1[4]
    if 0.0 != s:
        r2[4] -= m2 * s; r3[4] -= m3 * s
    s = r1[5]
    if 0.0 != s:
        r2[5] -= m2 * s; r3[5] -= m3 * s
    s = r1[6]
    if 0.0 != s:
        r2[6] -= m2 * s; r3[6] -= m3 * s
    s = r1[7]
    if 0.0 != s:
        r2[7] -= m2 * s; r3[7] -= m3 * s

    # choose pivot - or die 
    if abs(r3[2]) > abs(r2[2]):
        swap_rows(r3, r2)
    if 0.0 == r2[2]:
        return False

    # eliminate third variable */
    m3 = r3[2] / float(r2[2])
    r3[3] -= m3 * r2[3]; r3[4] -= m3 * r2[4]
    r3[5] -= m3 * r2[5]; r3[6] -= m3 * r2[6]
    r3[7] -= m3 * r2[7]

    # last check
    if 0.0 == r3[3]:
        return False

    s = 1.0 / r3[3] # now back substitute row 3 
    r3[4] *= s; r3[5] *= s; r3[6] *= s; r3[7] *= s

    m2 = r2[3] # now back substitute row 2 
    s  = 1.0 / r2[2]
    r2[4] = s * (r2[4] - r3[4] * m2); r2[5] = s * (r2[5] - r3[5] * m2)
    r2[6] = s * (r2[6] - r3[6] * m2); r2[7] = s * (r2[7] - r3[7] * m2)
    m1 = r1[3]
    r1[4] -= r3[4] * m1; r1[5] -= r3[5] * m1
    r1[6] -= r3[6] * m1; r1[7] -= r3[7] * m1
    m0 = r0[3]
    r0[4] -= r3[4] * m0; r0[5] -= r3[5] * m0
    r0[6] -= r3[6] * m0; r0[7] -= r3[7] * m0

    m1 = r1[2]  # now back substitute row 1 
    s  = 1.0 / r1[1]
    r1[4] = s * (r1[4] - r2[4] * m1); r1[5] = s * (r1[5] - r2[5] * m1)
    r1[6] = s * (r1[6] - r2[6] * m1); r1[7] = s * (r1[7] - r2[7] * m1)
    m0 = r0[2]
    r0[4] -= r2[4] * m0; r0[5] -= r2[5] * m0
    r0[6] -= r2[6] * m0; r0[7] -= r2[7] * m0

    m0 = r0[1] # now back substitute row 0 
    s  = 1.0 / r0[0]
    r0[4] = s * (r0[4] - r1[4] * m0); r0[5] = s * (r0[5] - r1[5] * m0)
    r0[6] = s * (r0[6] - r1[6] * m0); r0[7] = s * (r0[7] - r1[7] * m0)

    dst[rc(0,0)] = r0[4]; dst[rc(0,1)] = r0[5]
    dst[rc(0,2)] = r0[6]; dst[rc(0,3)] = r0[7]
    dst[rc(1,0)] = r1[4]; dst[rc(1,1)] = r1[5]
    dst[rc(1,2)] = r1[6]; dst[rc(1,3)] = r1[7]
    dst[rc(2,0)] = r2[4]; dst[rc(2,1)] = r2[5]
    dst[rc(2,2)] = r2[6]; dst[rc(2,3)] = r2[7]
    dst[rc(3,0)] = r3[4]; dst[rc(3,1)] = r3[5]
    dst[rc(3,2)] = r3[6]; dst[rc(3,3)] = r3[7]
    
    return True

def c_transform_vector3(vout, v, m):
    vout[0] = m[0] * v[0] + m[4] * v[1] + m[8] *  v[2] + m[12]
    vout[1] = m[1] * v[0] + m[5] * v[1] + m[9] *  v[2] + m[13]
    vout[2] = m[2] * v[0] + m[6] * v[1] + m[10] * v[2] + m[14]

def c_transform_vector4(vout, v, m):
    vout[0] = m[0] * v[0] + m[4] * v[1] + m[8] *  v[2] + m[12] * v[3]
    vout[1] = m[1] * v[0] + m[5] * v[1] + m[9] *  v[2] + m[13] * v[3]
    vout[2] = m[2] * v[0] + m[6] * v[1] + m[10] * v[2] + m[14] * v[3]
    vout[3] = m[3] * v[0] + m[7] * v[1] + m[11] * v[2] + m[15] * v[3]


#def c_identity44(dout=None):
#    if not dout:
#

def rotated_z(v, angle):
    if not angle:
        return v

    sin_angle = math.sin( math.pi * angle / 180. )
    cos_angle = math.cos( math.pi * angle / 180. )
    
    return euclid.Vector3(
        v[0] * cos_angle - v[1] * sin_angle,
        v[0] * sin_angle + v[1] * cos_angle,
        v[2])

def rotated_y(v, angle):
    if not angle:
        return v

    sin_angle = math.sin( math.pi * angle / 180. )
    cos_angle = math.cos( math.pi * angle / 180. )
    
    return euclid.Vector3(
        v[0] * cos_angle + v[2] *sin_angle,
        v[1],
        -v[0] * sin_angle + v[2] *cos_angle)


