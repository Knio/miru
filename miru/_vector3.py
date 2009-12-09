# Modified and stripped down version of euclid.by.
# The original version of eculid.py can be found here: 
# http://code.google.com/p/pyeuclid/

##########################################################################
#### This is terrible hack reflecting my inability to use
#### voodoo magic or such to make euclid.Vector3 a new-style
#### class and thus be able to monitor changes on x,y,z
#### properties. etc. etc.
##########################################################################

import math
import operator

def update_parent(m):
    def _m(self, x):
        m(self, x)
        if self._parent and self._attr:
            setattr(self._parent, self._attr, self)
    return _m

class Vector3(object):
    _last_value = None
    _parent = None

    def __init__(self, x, y, z, parent=None, attr=None):
        self._x = x
        self._y = y
        self._z = z

        self._parent = parent
        self._attr = attr

    def _getx(self):
        return self._x

    @update_parent
    def _setx(self, x):
        v = Vector3(x - self._x, 0, 0)
        self.__iadd__(v)

    x = property(_getx, _setx)
    
    def _gety(self):
        return self._y

    @update_parent
    def _sety(self, y):
        v = Vector3(0, y - self._y, 0)
        self.__iadd__(v)

    y = property(_gety, _sety)
    
    def _getz(self):
        return self._z

    @update_parent
    def _setz(self, z):
        v = Vector3(0, 0, z - self._z)
        self.__iadd__(v)

    z = property(_getz, _setz)

    def __copy__(self):
        return self.__class__(self._x, self._y, self._z)

    copy = __copy__

    def __repr__(self):
        return 'Vector3(%.2f, %.2f, %.2f)' % (self._x,
                                              self._y,
                                              self._z)

    def __eq__(self, other):
        if isinstance(other, Vector3):
            return self._x == other.x and \
                   self._y == other.y and \
                   self._z == other.z
        else:
            assert hasattr(other, '__len__') and len(other) == 3
            return self._x == other[0] and \
                   self._y == other[1] and \
                   self._z == other[2]

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self._x != 0 or self._y != 0 or self._z != 0

    def __len__(self):
        return 3

    def __getitem__(self, key):
        return (self._x, self._y, self._z)[key]

    def __setitem__(self, key, value):
        l = [self._x, self._y, self._z]
        l[key] = value
        self._x, self._y, self._z = l

    def __iter__(self):
        return iter((self._x, self._y, self._z))



    def __getattr__(self, name):
        try:
            return tuple([(self._x, self._y, self._z)['xyz'.index(c)] \
                          for c in name])
        except ValueError:
            raise AttributeError, name


    def __add__(self, other):
        if isinstance(other, Vector3):
            # Vector + Vector -> Vector
            # Vector + Point -> Point
            # Point + Point -> Vector
            if self.__class__ is other.__class__:
                _class = Vector3
            else:
                _class = Point3
            return _class(self._x + other.x,
                          self._y + other.y,
                          self._z + other.z)
        else:
            assert hasattr(other, '__len__') and len(other) == 3
            return Vector3(self._x + other[0],
                           self._y + other[1],
                           self._z + other[2])
    __radd__ = __add__

    def __iadd__(self, other):
        self._last_value = tuple(self)

        if isinstance(other, Vector3):
            self._x += other.x
            self._y += other.y
            self._z += other.z
        else:
            self._x += other[0]
            self._y += other[1]
            self._z += other[2]
        return self
    
    def __isub__(self, other):
        v = Vector3(*other)
        return self.__iadd__(-1 * v)

    def __sub__(self, other):
        if isinstance(other, Vector3):
            # Vector - Vector -> Vector
            # Vector - Point -> Point
            # Point - Point -> Vector
            if self.__class__ is other.__class__:
                _class = Vector3
            else:
                _class = Point3
            return Vector3(self._x - other.x,
                           self._y - other.y,
                           self._z - other.z)
        else:
            assert hasattr(other, '__len__') and len(other) == 3
            return Vector3(self._x - other[0],
                           self._y - other[1],
                           self._z - other[2])

   
    def __rsub__(self, other):
        if isinstance(other, Vector3):
            return Vector3(other.x - self._x,
                           other.y - self._y,
                           other.z - self._z)
        else:
            assert hasattr(other, '__len__') and len(other) == 3
            return Vector3(other.x - self[0],
                           other.y - self[1],
                           other.z - self[2])

    def __mul__(self, other):
        if isinstance(other, Vector3):
            # TODO component-wise mul/div in-place and on Vector2; docs.
            if self.__class__ is Point3 or other.__class__ is Point3:
                _class = Point3
            else:
                _class = Vector3
            return _class(self._x * other.x,
                          self._y * other.y,
                          self._z * other.z)
        else:
            assert type(other) in (int, long, float)
            return Vector3(self._x * other,
                           self._y * other,
                           self._z * other)

    __rmul__ = __mul__

    def __imul__(self, other):
        self._last_value = tuple(self)

        assert type(other) in (int, long, float)
        self._x *= other
        self._y *= other
        self._z *= other
        return self

    def __div__(self, other):
        assert type(other) in (int, long, float)
        return Vector3(operator.div(self._x, other),
                       operator.div(self._y, other),
                       operator.div(self._z, other))


    def __rdiv__(self, other):
        assert type(other) in (int, long, float)
        return Vector3(operator.div(other, self._x),
                       operator.div(other, self._y),
                       operator.div(other, self._z))

    def __floordiv__(self, other):
        assert type(other) in (int, long, float)
        return Vector3(operator.floordiv(self._x, other),
                       operator.floordiv(self._y, other),
                       operator.floordiv(self._z, other))


    def __rfloordiv__(self, other):
        assert type(other) in (int, long, float)
        return Vector3(operator.floordiv(other, self._x),
                       operator.floordiv(other, self._y),
                       operator.floordiv(other, self._z))

    def __truediv__(self, other):
        assert type(other) in (int, long, float)
        return Vector3(operator.truediv(self._x, other),
                       operator.truediv(self._y, other),
                       operator.truediv(self._z, other))


    def __rtruediv__(self, other):
        assert type(other) in (int, long, float)
        return Vector3(operator.truediv(other, self._x),
                       operator.truediv(other, self._y),
                       operator.truediv(other, self._z))
    
    def __neg__(self):
        return Vector3(-self._x,
                        -self._y,
                        -self._z)

    __pos__ = __copy__
    
    def __abs__(self):
        return math.sqrt(self._x ** 2 + \
                         self._y ** 2 + \
                         self._z ** 2)

    magnitude = __abs__

    def magnitude_squared(self):
        return self._x ** 2 + \
               self._y ** 2 + \
               self._z ** 2

    def normalize(self):
        d = self.magnitude()
        if d:
            self._x /= d
            self._y /= d
            self._z /= d
        return self

    def normalized(self):
        d = self.magnitude()
        if d:
            return Vector3(self._x / d,
                           self._y / d,
                           self._z / d)
        return self.copy()

    def dot(self, other):
        return self._x * other.x + \
               self._y * other.y + \
               self._z * other.z

    def cross(self, other):
        return Vector3(self._y * other.z - self._z * other.y,
                       -self._x * other.z + self._z * other.x,
                       self._x * other.y - self._y * other.x)

    def reflect(self, normal):
        # assume normal is normalized
        d = 2 * (self._x * normal.x + self._y * normal.y + self._z * normal.z)
        return Vector3(self._x - d * normal.x,
                       self._y - d * normal.y,
                       self._z - d * normal.z)


