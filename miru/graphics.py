import ctypes
import os

import euclid

import pyglet.gl as gl
import pyglet

from miru import math3d
from miru import core

vector_4f = ctypes.c_float * 4

class ColorMaterialGroup(pyglet.graphics.Group):
    """
    L{pyglet.graphics.Group} implementation for enabling GL_COLOR_MATERIAL.
    This is the default parent group for L{ColorGroup}.  Generally you do
    not need to use this class directly.
    """

    def __init__(self, parent=None, material_args=None, lighting=True):
        super(ColorMaterialGroup, self).__init__(parent=parent)
        self.material_args = (material_args or
                              (gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE))
        self.lighting = lighting

    def set_state(self):
        gl.glPushAttrib( gl.GL_ENABLE_BIT )
        gl.glEnable( gl.GL_COLOR_MATERIAL )
        if not self.lighting:
            gl.glDisable( gl.GL_LIGHTING )
        gl.glColorMaterial(*self.material_args)

    def unset_state(self):
        gl.glPopAttrib()

_color_material_group = ColorMaterialGroup()

class ColorGroup(pyglet.graphics.Group):
    """
    L{pyglet.graphics.Group} useful for coloring a group of objects.
    An example rendering a green sphere:

        from miru.geom import Sphere, get_vlist
        sphere_geom = Sphere()
        green_group = ColorGroup([0.5, 1.0, 0.5])
        batch = pyglet.graphics.Batch()
        get_vlist(sphere_geom, batch, green_group)
    """

    def __init__(self, color, parent=None):
        """
        @param color: The color to set which can be one of
            * 4-tuple to RGBA values
            * 3-tuple to specify RGB values
            * 2-tuple to specify LA (luminance + apha) values
            * An int/float to specify L (luminance)  value
          Each value for RGBA or L should be range [0.0, 1.0]. 
        """
        if not parent:
            parent = _color_material_group
        super(ColorGroup, self).__init__( parent=parent )

        self.color = color # Default RGBA
        if type(color) in (float, int): # Luminance
            self.color = [color] * 3 + [1]
        else:
            color = list(color)
            if len(color) == 3: # RGB
                self.color = color + [1]
            elif len(color) == 2: # Luminance Alpha
                self.color = [color[0]] * 3 + [color[1]]

    def set_state(self):
        gl.glColor4f(*self.color)

    def unset_state(self):
        gl.glColor4f(1,1,1,1)



class TextureEnableGroup(pyglet.graphics.Group):
    """
    L{pyglet.graphics.Group} implementation for enabling texture support.
    The default target is C{GL_TEXTURE_2D}.  This is the default
    parent group for L{TextureBindGroup}.  Generally you do not need
    to use this class directly.
    """

    def __init__(self, target=gl.GL_TEXTURE_2D):
        """
        @param target: The texture flag to enable (GL_TEXTURE_2D)
        """
        super(TextureEnableGroup, self).__init__()
        self.target = target

    def set_state(self):
        gl.glEnable(self.target)
        
    def unset_state(self):
        gl.glDisable( self.target )

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.target == other.target)

_tex_enable_group = TextureEnableGroup#()
tex_enable_group_2D = _tex_enable_group
tex_enable_group_1D = TextureEnableGroup#(target=gl.GL_TEXTURE_1D)

class SphereMapGroup(pyglet.graphics.Group):

    def __init__(self, texture):
        super(SphereMapGroup, self).__init__(parent=_tex_enable_group(target=texture.target))
        self.texture = texture

    def set_state(self):
        gl.glTexGeni( gl.GL_S, gl.GL_TEXTURE_GEN_MODE, gl.GL_SPHERE_MAP )
        gl.glTexGeni( gl.GL_T, gl.GL_TEXTURE_GEN_MODE, gl.GL_SPHERE_MAP )
        gl.glEnable( gl.GL_TEXTURE_GEN_S )
        gl.glEnable( gl.GL_TEXTURE_GEN_T )
        gl.glBindTexture( gl.GL_TEXTURE_2D, self.texture.id )

    def unset_state(self):
        gl.glDisable( gl.GL_TEXTURE_GEN_T )
        gl.glDisable( gl.GL_TEXTURE_GEN_S )

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.texture == other.texture and
                self.parent == other.parent)

SphereMappingGroup = SphereMapGroup

class ProjectionTextureGroup(pyglet.graphics.Group):


    def __init__(self, texture, plane=None):
        super(ProjectionTextureGroup, self).__init__(parent=_tex_enable_group(target=texture.target))
        self.plane = plane
        if plane:
            self.plane = (gl.GLfloat * 4)(*plane)
        self.texture = texture

    def set_state(self):
        gl.glTexGeni( gl.GL_S, gl.GL_TEXTURE_GEN_MODE, gl.GL_EYE_LINEAR )
        gl.glTexGeni( gl.GL_T, gl.GL_TEXTURE_GEN_MODE, gl.GL_EYE_LINEAR )

        if self.plane:
            gl.glTexGenfv(gl.GL_S, gl.GL_EYE_PLANE, self.plane)
            gl.glTexGenfv(gl.GL_T, gl.GL_EYE_PLANE, self.plane)

        gl.glEnable( gl.GL_TEXTURE_GEN_S )
        gl.glEnable( gl.GL_TEXTURE_GEN_T )

        gl.glDepthMask( gl.GL_TRUE )
        gl.glBindTexture( gl.GL_TEXTURE_2D, self.texture.id )

    def unset_state(self):
        gl.glDisable( gl.GL_TEXTURE_GEN_T )
        gl.glDisable( gl.GL_TEXTURE_GEN_S )

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.texture == other.texture)

class ObjectLinearTextureGroup(pyglet.graphics.Group):

    plane = (gl.GLfloat * 4)(0., 0., 1, 0.)

    def __init__(self, texture, plane=None):
        super(ObjectLinearTextureGroup, self).__init__(parent=_tex_enable_group(texture=texture.target))
        self.texture = texture
        self.plane = plane and (gl.GLfloat * 4)(*plane[:]) or self.plane

    def set_state(self):
        gl.glTexGeni( gl.GL_S, gl.GL_TEXTURE_GEN_MODE, gl.GL_OBJECT_LINEAR )
        gl.glTexGeni( gl.GL_T, gl.GL_TEXTURE_GEN_MODE, gl.GL_OBJECT_LINEAR )

        gl.glTexGenfv(gl.GL_S, gl.GL_OBJECT_PLANE, self.plane)
        gl.glTexGenfv(gl.GL_T, gl.GL_OBJECT_PLANE, self.plane)

        gl.glEnable( gl.GL_TEXTURE_GEN_S )
        gl.glEnable( gl.GL_TEXTURE_GEN_T )

        gl.glDepthMask( gl.GL_TRUE )
        gl.glBindTexture( gl.GL_TEXTURE_2D, self.texture.id )

    def unset_state(self):
        gl.glDisable( gl.GL_TEXTURE_GEN_T )
        gl.glDisable( gl.GL_TEXTURE_GEN_S )

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.texture == other.texture)

class ReflectionMapTextureGroup(pyglet.graphics.Group):

    def __init__(self, tex_object):
        super(ReflectionMapTextureGroup, self).__init__()
        self.tex_object = tex_object

    def set_state(self):
        gl.glBindTexture( gl.GL_TEXTURE_CUBE_MAP, self.tex_object )
        gl.glTexGeni( gl.GL_S, gl.GL_TEXTURE_GEN_MODE, gl.GL_REFLECTION_MAP )
        gl.glTexGeni( gl.GL_T, gl.GL_TEXTURE_GEN_MODE, gl.GL_REFLECTION_MAP )
        gl.glTexGeni( gl.GL_R, gl.GL_TEXTURE_GEN_MODE, gl.GL_REFLECTION_MAP )
        gl.glEnable( gl.GL_TEXTURE_CUBE_MAP )
        gl.glTexEnvi( gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_DECAL )

#reflmap_texture_group = ReflectionMapTextureGroup()

class GenCoordTextureGroup(pyglet.graphics.Group):

    def __init__(self, parent=None):
        super(GenCoordTextureGroup, self).__init__(parent=parent)

    def set_state(self):# experimental texture positioning
        #border_color = vector_4f(0.0, 0.0, 0.0, 0.0)
        #gl.glTexParameterfv(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BORDER_COLOR, border_color)
        #gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        #gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        #gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        #gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        #gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)
        gl.glEnable( gl.GL_TEXTURE_GEN_S )
        gl.glEnable( gl.GL_TEXTURE_GEN_T )
        gl.glEnable( gl.GL_TEXTURE_GEN_R )

    def unset_state(self):
        gl.glDisable( gl.GL_TEXTURE_GEN_R )
        gl.glDisable( gl.GL_TEXTURE_GEN_T )
        gl.glDisable( gl.GL_TEXTURE_GEN_S )


class TextureTransformGroup(pyglet.graphics.Group):

    def __init__(self, texture=None, group=None,
                 translation=None, rotation=None):
        if not group:
            group = TextureBindGroup(texture)
        super(TextureTransformGroup, self).__init__(parent=group)
        self.translation = translation
        self.rotation = rotation

    def set_state(self):
        gl.glPushMatrix()
        gl.glMatrixMode( gl.GL_TEXTURE )
        gl.glLoadIdentity()
        if self.translation:
            gl.glTranslatef(*self.translation)
        if self.rotation:
            gl.glRotatef(self.rotation[0], 0, 0, 1)
            gl.glRotatef(self.rotation[1], 0, 1, 0)
            gl.glRotatef(self.rotation[2], 1, 0, 0)
        gl.glMatrixMode( gl.GL_MODELVIEW )

    def unset_state(self):
        gl.glPopMatrix()
        gl.glMatrixMode( gl.GL_TEXTURE )
        gl.glLoadIdentity()
        gl.glMatrixMode( gl.GL_MODELVIEW )


class TextureBindGroup(pyglet.graphics.Group):
    """
    L{pyglet.graphics.Group} implementation for binding a texture object.
    Example binding a texture to cube:

        from pyglet.graphics import Batch
        from pyglet.image import load as load_image
        from miru.ext.geom import Cube, get_vlist

        batch = Batch()
        cube_geom = Cube()
        tex = load_image('image.png').get_texture()
        texture_group = TextureBindGroup(tex)
        get_vlist(cube_geom, batch, texture_group)
    """

    def __init__(self, texture, target=gl.GL_TEXTURE_2D,
                 parent=None, gencoords=False):
        """
        @param texture: instance of C{pylget.image.Texture} or integer
            id of the texture object
        @param target: texture target (default: GL_TEXTURE_2D)
        @param parent: parent group (default: L{TextureEnableGroup} instance)
        @param gencoords: generate coordinates flag - if C{True}, L{GenCoordTextureGroup}
            instance is used as immediate parent
        """
        if gencoords:
            parent = GenCoordTextureGroup(
                parent=(parent or _tex_enable_group(target=target)))
        else:
            parent = parent or _tex_enable_group(target=target)
        super(TextureBindGroup, self).__init__(parent=parent)
        self.target = target
        self.texture = texture
        if not isinstance(texture, pyglet.image.Texture):
            class _PseudoTexture(object):
                def __init__(self, id):
                    self.id = id
            self.texture = _PseudoTexture(texture)

    def set_state(self):
        gl.glColor3f(1,1,1)
        gl.glBindTexture(self.target, self.texture.id)

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.texture == other.texture and
                self.parent == other.parent)


class PointSpriteGroup(pyglet.graphics.Group):
    """
    L{pyglet.graphics.Group} implementation for enabling point sprites (GL_POINT_SPRITE).
    (Note, this does not test for support).
    """

    def __init__(self, texture, point_size=16, attenuate=False, parent=None):
        """
        @param texture: instance of L{pyglet.image.Texture}
        @param point_size: the point size
        @param attenuate: use quadratic attenuation (default: False)
        @param parent: the parent group (default: C{TextureEnableGroup})
        """
        if not parent:
            parent = _tex_enable_group(target=texture.target)
        super(PointSpriteGroup, self).__init__(parent=parent)
        self.texture = texture
        self.attenuate = attenuate
        self.point_size = point_size

    def set_state(self):
        gl.glPushAttrib( gl.GL_ENABLE_BIT )
        gl.glBindTexture( gl.GL_TEXTURE_2D, self.texture.id )
        gl.glEnable( gl.GL_POINT_SPRITE )
        gl.glDisable( gl.GL_LIGHTING )

        if self.attenuate:
            quadratic = (gl.GLfloat * 3)()
            quadratic[:] = (1.0, 0.0, 0.01)
            gl.glPointParameterfv( gl.GL_POINT_DISTANCE_ATTENUATION, quadratic )

        max_size = gl.GLfloat()
        gl.glGetFloatv( gl.GL_POINT_SIZE_MAX, max_size )

        gl.glPointParameterf( gl.GL_POINT_FADE_THRESHOLD_SIZE, 60.0 )

        gl.glPointParameterf( gl.GL_POINT_SIZE_MIN, 1.0 )
        gl.glPointParameterf( gl.GL_POINT_SIZE_MAX, max_size )

        gl.glTexEnvf( gl.GL_POINT_SPRITE, gl.GL_COORD_REPLACE, gl.GL_TRUE )
        gl.glPointSize( self.point_size )


        #gl.glTexEnvf( GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE )

    def unset_state(self):
        gl.glPopAttrib()



class CellShaderGroup(pyglet.graphics.Group):

    def __init__(self, texobj, color_table, width, format,
                 internalformat=None, parent=None):
        parent = parent or tex_enable_group_1D(target=gl.GL_TEXTURE_1D)
        super(CellShaderGroup, self).__init__(parent=parent)
        self.internalformat = internalformat or format
        self.color_table = color_table
        self.width = width
        self.format = format
        self.texobj = texobj

    def set_state(self):
        gl.glBindTexture( GL_TEXTURE_1D, self.texobj )
        #gl.glTexImage1D( gl.GL_TEXTURE_1D, 0, self.internalformat, self.width, 0, self.format,
        #    gl.GL_UNSIGNED_BYTE, self.color_table )

def get_wrapped_texture(img):
    """Convenience method which get's texture from image and sets up 
    parameters to enable wrapping along S and T coordinates.  You should
    use this function for getting textures to be used with
    C{SphereMapGroup}, C{EyeLinearMapGroup} or other texture groups.
    """
    # TODO - test whether or not pyglet's chaching of the texture
    # would present any problems when using the texture otherwise.
    tex = img.get_texture()
    gl.glTexParameteri( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT )
    gl.glTexParameteri( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT )
    gl.glTexParameteri( gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR )
    return tex


class MeshBuilder(object):
    """
    MeshBuilder supplies utilitiy functions for loading mesh data from
    external files, applying transforms over vertex data and adding
    mesh data to your own batches.

    Currently only Wavefront OBJ files are supported - and
    a subset of the OBJ specification.

    Example usage:

        from pyglet.graphics import Batch

        batch = Batch()
        mesh_id = MeshBuilder.load('object.obj')
        MeshBuilder.add_to_batch(mesh_id, batch)


    Aliases for the class methods are also available:

        mesh_id = load_mesh('object.obj')
        batch_mesh(mesh_id, batch)
    """

    WAVEFRONT = 0

    TYPES = {'obj': WAVEFRONT}

    _key = 0
    _loaded = {}
    _texbind_groups = {}
    _wobj_load_cache = {}

    @classmethod
    def load(cls, filename, type=None, mesh_id=None, flip_normals=False):
        """
        Load mesh data from a file.  The only type currently supported
        is MeshBuilder.WAVEFRONT.

        (alias: L{miru.graphics.load_mesh})

        @param filename: filename containing mesh data (e.g. test.obj)
        @param type: The format (default: WAVEFRONT)
        @oaram mesh_id: Can be specified as any hashable value. Otherwise, an
            internal sequence number is assigned.
        @flip_normals: mostly a hack to flip normal vectors for messed up
            exports (default: False)
        @return: the mesh id
        """
        if type is None:
            ext = os.path.splitext(filename)[1][1:]
            type = cls.TYPES.get(ext, -1)
        if type not in cls.TYPES.values():
            raise ValueError, 'Unsupported type: %d' % type
        (count, data, mode, tex_filename) = cls._load_wfobj(
            filename, flip_normals=flip_normals)
        if mesh_id is None:
            mesh_id = MeshBuilder._gen_mesh_id()
        cls._loaded[mesh_id] = (count, data, mode, tex_filename)
        return mesh_id


    # TODO - add matrix as optional argument to transform

    @classmethod
    def transform(cls, source_mesh_id,
                  translation=None, rotation=None, target_mesh_id=None):
        """
        Transform mesh vertices.  The original data is left intact and
        a new mesh is bound to target_mesh_id or the next aut

        @param source_mesh_id: The mesh id returned from C{MeshBuilder.load}
        @param translation: Sequence of length 3, specifying a translational 
                transform (optional)
        @param rotation: Sequence of length 3, specifying a rotational 
                transform (optional)
        @param target_mesh_id: Mesh id to store transformed vertex data under
                (optional)
        """
        (count, data, mode, tex_filename) = cls._loaded[source_mesh_id]
        # TODO - optional c optimization or use numeric
        # Also - for pure-python scenarios, enable filesystem caching
        # for faster restarts?
        vertices = data[0][1][:]
        if translation:
            for idx in xrange(0, len(vertices), 3):
                vertices[idx] += translation[0]
                vertices[idx+1] += translation[1]
                vertices[idx+2] += translation[2]
        if rotation:
            raise NotImplementedError, "roate not currently supported"

        updated_data = list(data)
        updated_data[0] = list(updated_data[0])
        updated_data[0][1] = vertices
        updated_data[0] = tuple(updated_data[0])

        if target_mesh_id is None:
            target_mesh_id = cls._gen_mesh_id()
        cls._loaded[target_mesh_id] = (count, updated_data,
                                       mode, tex_filename)
        return target_mesh_id


    @classmethod
    def get_data(cls, mesh_id):
        """Returns 3-tuple consising of loaded vertex count, vertex data (in format
        of sent to C{pyglet.graphics.vertex_list}) the mode (GL_QUADS or GL_TRIANGLES)
        for drawing.

        @param mesh_id: The mesh id returned from C{MeshBuilder.load}
        """
        return cls._loaded[mesh_id][:3]

    @classmethod
    def add_to_batch(cls, mesh_id, batch, group=None, parent_texture=True):
        """Add loaded mesh data to batch and optional group for data loaded for key.

        @param mesh_id: The mesh id returned from C{MeshBuilder.load}
        @param batch: The batch to add vertex data to
        @type batch: C{pyglet.graphics.Batch}
        @param group: Optional group
        @type group: C{pyglet.graphics.Group}
        @parent parent_texture: If True and the group is not an
            instance of C{miru.graphics.TextureBindGroup}, create new
            TextureBindGroup for the mesh and set its parent to group.
        """
        (count, data, mode, tex_filename) = cls._loaded[mesh_id]
        if not group and tex_filename:
            group = cls._get_texbind_group(tex_filename)
        if group and parent_texture and tex_filename:
            if group.__class__ != TextureBindGroup:
                # don't use cached group since we might clobber the parent
                #img = pyglet.image.load( tex_filename )
                #tex = img.get_texture()
                tex_group = TextureBindGroup(
                    pyglet.image.load( tex_filename).get_texture() )
                group.parent = tex_group
        dt = [ (d[0], d[1][:]) for d in data ]
        batch.add(count, mode, group, *dt)


    @classmethod
    def _get_texbind_group(cls, filename):
        group = cls._texbind_groups.get(filename)
        if not group:
            group = TextureBindGroup(
                pyglet.image.load(filename).get_texture() )
            cls._texbind_groups[filename] = group
        return group

    @classmethod
    def get_vlist(cls, mesh_id):
        """Returns 2-tuple consisting of a new vertex list and the mode (GL_TRIANGLES
        or GL_QUADS) to use when drawing.

        @param mesh_id: The mesh id returned from C{MeshBuilder.load}
        """
        (count, data, mode, tex_filename) = cls._loaded[mesh_id]
        return pyglet.graphics.vertex_list(count, *data), mode

    @classmethod
    def _gen_mesh_id(cls):
        key = cls._key
        cls._key += 1
        return key

    @classmethod
    def _load_wfobj(cls, filename, flip_normals=False):
        import miru.tools.obj

        if (filename, flip_normals) in cls._wobj_load_cache:
            return cls._wobj_load_cache[(filename, flip_normals)]

        parser = miru.tools.obj.ObjParser(
            filename, flip_normals=flip_normals)
        obj, objects, data = parser.parse()

        vs = []
        tcs = []
        nmls = []
        # TODO  Support without texcoords
        for (vidxs, tidxs, nidxs) in zip(
            obj.vertex_indices, obj.texcoord_indices, obj.normal_indices ):
            for (idx, tidx, nidx) in zip( vidxs, tidxs, nidxs ):
                vs.extend( obj.vertices[idx] )
                tcs.extend( obj.texcoords[tidx] )
                nmls.extend( obj.normals[nidx] )

        teximg_filename = None
        if obj.material and obj.material.teximg_filename:
            teximg_filename = obj.material.teximg_filename

        if len(obj.vertices[0]) == 4: # Quad
            count = len( vs ) / 4
            mode = gl.GL_QUADS
        else: # Triangle
            count = len( vs ) / 3
            mode = gl.GL_TRIANGLES


        data = [ ('v3f', vs), ('t2f', tcs), ('n3f', nmls) ]
        #vlist = pyglet.graphics.vertex_list(count, data)
        cls._wobj_load_cache[(filename, flip_normals)] = (count, data,
                                                          mode, teximg_filename)
        return (count, data, mode, teximg_filename)

# Aliases - I recommend using these as `functions' instead of
# MeshBuilder.load(...) etc.

load_mesh = MeshBuilder.load

mesh_transform = MeshBuilder.transform

mesh_data = MeshBuilder.get_data

mesh_vlist = MeshBuilder.get_vlist

batch_mesh = MeshBuilder.add_to_batch


def load_wobj(path, batch=None, group=None):
    """Quick and dirty - but not always most efficient - way
    to load wavefront object files.
    """
    mesh_id = load_mesh(path)
    b = batch or pyglet.graphics.Batch()
    batch_mesh(mesh_id, b, group=group)
    if batch is None:
        return core.Object(b)
    return group

class DisplayList(object):

    def __init__(self, drawf):
        self.list_id = gl.glGenLists( 1 )
        gl.glNewList( self.list_id, gl.GL_COMPILE )
        drawf()
        gl.glEndList()


    def draw(self):
        gl.glCallList( self.list_id )


class Cubemap(object):


    def __init__(self, images, format=None):

        assert len(images) == 6

        refimg = pyglet.image.load( images[0] )

        # Create a new texture binding for this cubemap
        self.texture_id = gl.GLuint()
        gl.glGenTextures(1, ctypes.byref( self.texture_id ))
        gl.glBindTexture( gl.GL_TEXTURE_CUBE_MAP, self.texture_id )

        if format is None:
            format = {
                'RGB': gl.GL_RGB,
                'RGBA': gl.GL_RGBA,
                'L': gl.GL_LUMINANCE,
                'LA': gl.GL_LUMINANCE_ALPHA,
                'A': gl.GL_ALPHA,
                'BGR': gl.GL_BGR,
                'BGRA': gl.GL_BGRA
                }[ refimg.format ]

        for param in (
            ( gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR ),
            ( gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR ),
            ( gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE ),
            ( gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE ),
            ( gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE )):
            gl.glTexParameteri(*param)
        for (idx, cube) in enumerate((
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X,
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
            gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z)):
            img = pyglet.image.load( images[idx] )
            gl.glTexParameteri( gl.GL_TEXTURE_CUBE_MAP, gl.GL_GENERATE_MIPMAP, gl.GL_TRUE )
            img.blit_to_texture( cube, 0, 0, 0, 0, format )

        self.texture_group_a = ReflectionMapTextureGroup(self.texture_id)
        self.texture_group_b = GenCoordTextureGroup(
            parent=self.texture_group_a)


class CellShader(object):
    """CellShader is a work in process and still needs several `bits' before
    it can be deemed completed.  Currently, it is no more than simple application
    of 1D texture mappping using diffuse surface reflection (or `dot product lighting')
    over registered color tables.

    The key ingredition to making this a true CellShader is of course outlining.
    """

    def __init__(self, light_dir=None):
        self._tables= {}
        self._scheduled_vlists = []
        self._texobjects = {}
        self._defaultgroups = {}
        self.light_dir = light_dir or (0.0, 1.0, 0.0)
        self._batch = None
        self._batches = []

    def create_color_table(self, max_color, rows=4, blend_alpha=False,
                           intensity_range=(0.3,1.0)):
        """

        @return: C{c_float} array sized `rows' * `len(max_color)' 
        """

        if type(max_color) in (int, float):
            max_color = (max_color, max_color, max_color)
        max_color = tuple(max_color)

        k = (max_color, rows, blend_alpha, intensity_range)
        table = self._tables.get(k)

        if not table:
            assert (    intensity_range[1] <= 1.0 
                        and intensity_range[1] >= 0.0
                        and intensity_range[1] >= intensity_range[0]
                        and intensity_range[0] >= 0.0 )
            table = self._build_color_table(*k)
            self._tables[k] = table
        return table

    def _build_color_table(self, max_color, rows, blend_alpha, intensity_range):
        count = len(max_color)
        is_alpha = count in (2,4)

        table = (gl.GLbyte * (count * rows))()

        (max_channel, max_channel_idx) = max(
            [(float(v),idx) for (idx,v) in enumerate(max_color)])

        factors = [0.0] * count
        if max_channel:
            factors[max_channel_idx] = 1.0
            for (idx, channel) in enumerate(max_color):
                if idx == max_channel_idx:
                    continue
                factor = channel / max_channel
                factors[idx] = factor
        else:
            table[:] = [0.] * (count * rows)

        window = intensity_range[1] - intensity_range[0]

        # This grading algorithm might be shit
        for idx in xrange(0, count * rows, count):
            # The second part of the predicate is weird, but this 
            # makes sure the user doesn't accidently skip blending th
            # B channel if format is RGB and blend_alpha=False
            if blend_alpha or (not blend_alpha and not is_alpha):
                #table[idx:idx+count] = max_color
                grade = intensity_range[0] + ((idx + 3) / float(count * rows)) * window
                channel_grades = [ (f * grade) for f in factors ]
                color = [ (c * g) for (c,g) in zip(max_color, channel_grades) ]
                for j in range(idx, idx+count):
                    table[j] = chr(color[j-idx] * 255)
        return table

    def create_texobject(self, color_table, format=gl.GL_RGB,
                         internalformat=gl.GL_RGB):

        k = (tuple(color_table), format, internalformat)
        texobj = self._texobjects.get(k)
        if texobj:
            return texobj

        width = {
            gl.GL_RGB: 3,
            gl.GL_RGBA: 4,
            gl.GL_LUMINANCE: 1,
            gl.GL_LUMINANCE_ALPHA: 2}[format]


        texobj = gl.GLuint()
        gl.glGenTextures( 1, ctypes.byref(texobj) )

        gl.glEnable( gl.GL_TEXTURE_1D )
        gl.glBindTexture( gl.GL_TEXTURE_1D, texobj )

        gl.glTexEnvi( gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_DECAL )
        gl.glTexParameteri( gl.GL_TEXTURE_1D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST )
        gl.glTexParameteri( gl.GL_TEXTURE_1D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST )
        gl.glTexParameteri( gl.GL_TEXTURE_1D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP )
        gl.glPixelStorei( gl.GL_UNPACK_ALIGNMENT, 1 )
        gl.glTexImage1D( gl.GL_TEXTURE_1D, 0, internalformat, width, 0, format,
                         gl.GL_UNSIGNED_BYTE, color_table )

        group = TextureBindGroup(texobj, target=gl.GL_TEXTURE_1D,
                                 parent=tex_enable_group_1D(target=gl.GL_TEXTURE_1D))
        #group = CellShaderGroup(texobj, color_table, width,
        #        format, internalformat)
        self._texobjects[k] = texobj
        self._defaultgroups[texobj.value] = group

        return texobj


    def get_texcoords(self, normals, texcoords=None):
        if not texcoords:
            texcoords = [0.] * (len(normals) // 3)

        inverted_light = (gl.GLfloat * 16)()
        mv_matrix = (gl.GLfloat * 16)()
        new_light = (gl.GLfloat * 3)()

        gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX, mv_matrix)
        math3d.c_invert_matrix4(inverted_light, mv_matrix)
        math3d.c_transform_vector3(new_light, self._light_dir, inverted_light)
        # TODO - compute and apply additional matrix inverse on object transformation
        new_light[0] -= inverted_light[12]
        new_light[1] -= inverted_light[13]
        new_light[2] -= inverted_light[14]
        # Need to check to see if we should explicitly free memory for this
        new_light = euclid.Vector3(*new_light[:]).normalized()

        for idx in xrange(0, len(normals), 3):
            normal = euclid.Vector3(*normals[idx:idx+3])
            texcoord = new_light.dot(normal)
            texcoords[idx // 3] = texcoord
        return texcoords

    update_texcoords = get_texcoords

    def add_vlist(self, count, mode, data, texobj, indices=None, batch=None, group=None):
        if not batch:
            batch = self.batch
        if not group:
            group = self._defaultgroups[texobj.value]
            print 'Using default group', group

        data = list(data)
        normals = [ d for (f,d) in data if 'n' in f ]
        # TODO - compute normal data over vertices ...
        assert normals, 'Normal data required!'
        normals = normals[0]
        texcoords = self.get_texcoords(normals)
        data.append(('t1f/stream', texcoords))

        if indices:
            vlist = batch.add_indexed(count, mode, group, indices, *data)
        else:
            vlist = batch.add(count, mode, group, *data)
        self._scheduled_vlists.append(vlist)


    def update(self, dt):
        for vlist in self._scheduled_vlists:
            self.update_texcoords(vlist.normals, vlist.tex_coords)

    def _get_light_dir(self):
        return self._light_dir[:]

    def _set_light_dir(self, light_dir):
        self._light_dir = (gl.GLfloat * 3)(*light_dir[:])

    light_dir = property(_get_light_dir, _set_light_dir)

    @property
    def batch(self):
        if not self._batch:
            self._batch = pyglet.graphics.Batch()
        return self._batch

cell_shader = CellShader()

class ShadowMap(core.PositionalMixin):

    def __init__(self, tex_unit=gl.GL_TEXTURE0, **kw):
        self.tex_unit = kw.pop('tex_unit', gl.GL_TEXTURE0)
        self.tex_matrix = None
        super(ShadowMap, self).__init__(**kw)

    def generate_map(self):
        scene_radius = 95.0
        light_to_scene_distance = math.sqrt(
            light_pos[0]**2 + light_pos[1]**2 + light_pos[2]**2)
        near_plane = light_to_scene_distance - scene_radius
        field_of_view = math3d.radians_to_degrees(2.0 *
                                                  math.atan(scene_radius / float(light_to_scene_distance)))

        tmp = (gl.GLfloat * 16)()

        gl.glMatrixMode( gl.GL_PROJECTION )
        gl.glLoadIdentity()
        gl.gluPerspective( field_of_view, 1.0, near_plane,
                           near_plane + (2.0 * scene_radius) )
        gl.glGetFloatv( gl.GL_PROJECTION_MATRIX, tmp )
        gl.light_projection = euclid.Matrix4()
        gl.light_projection[0:16] = tmp[:]

        # Switch to light's point of view
        gl.glMatrixMode( gl.GL_MODELVIEW )
        gl.glLoadIdentity()
        gl.gluLookAt( self.light.pos.x, self.light.pos.y, self.light.pos.z,
                      0.0, 0.0, 0.0, 0.0, 1.0, 0.0 )
        gl.glGetFloatv( gl.GL_MODELVIEW_MATRIX, tmp )
        light_mview = euclid.Matrix4()
        light_mview[0:16] = tmp[:]

        #glViewport(0, 0, shadow_width, shadow_height)

        # Clear the depth buffer only
        gl.glClear( gl.GL_DEPTH_BUFFER_BIT )

        # Remember the current shade model
        gl.glPushAttrib( gl.GL_ENABLE_BIT )
        prev_shade_model = cypes.GLint()
        gl.glGetIntegerv( gl.GL_SHADE_MODEL, prev_shade_model )

        # All we care about here is resulting depth values
        gl.glShadeModel( gl.GL_FLAT )
        gl.glDisable( gl.GL_LIGHTING )
        gl.glDisable( gl.GL_COLOR_MATERIAL )
        gl.glDisable( gl.GL_NORMALIZE )
        gl.glColorMask( 0, 0, 0, 0 )

        # Overcome imprecision
        gl.glEnable( gl.GL_POLYGON_OFFSET_FILL )

        #draw_models(False)
        self.context.render( exclude=self.exclude_shadows )

        # Copy depth values into depth texture
        gl.glCopyTexImage2D( gl.GL_TEXTURE_2D, 0, gl.GL_DEPTH_COMPONENT,
                             0, 0, shadow_width, shadow_height, 0 )

        # Restore normal drawing state
        gl.glShadeModel( gl.GL_SMOOTH )
        gl.glEnable( gl.GL_LIGHTING )
        gl.glEnable( gl.GL_COLOR_MATERIAL )
        gl.glEnable( gl.GL_NORMALIZE )
        gl.glColorMask( 1, 1, 1, 1 )
        gl.glDisable( gl.GL_POLYGON_OFFSET_FILL )

        # Setup up the texture matrix which will be use in eye-linear
        # texture mapping
        self.tex_matrix = euclid.Matrix4()
        self.tex_matrix.translate(0.5, 0.5, 0.5).scale(0.5, 0.5, 0.5)
        tmp_matrix.scale(0.5, 0.5, 0.5)
        tex_matrix = (tmp_matrix * light_projection) * light_mview
        self.tex_matrix.transpose()
        # Give us immediate access to ctypes arrays
        self.tex_matrix = (
            (gl.GLfloat * 4)(*self.tex_matrix[0:4]),
            (gl.GLfloat * 4)(*self.tex_matrix[4:8]),
            (gl.GLfloat * 4)(*self.tex_matrix[8:12]),
            (gl.GLfloat * 4)(*self.tex_matrix[12:16])
        )



class Image(object):
    """This is a proxy around C{pyglet.image.Image} which gives
    give appropriate ctype data for the following attributes:

        - format
        - data
    """

    def __init__(self, img):

        self._img = img
        if isinstance(img, str):
            self._img = pyglet.image.load(img)
        img = self._img

        self.format = {
            'RGB': gl.GL_RGB,
            'RGBA': gl.GL_RGBA,
            'L': gl.GL_LUMINANCE,
            'LA': gl.GL_LUMINANCE_ALPHA
            }[self._img.format]

        self.data = img.get_data(img.format, img.width * len(img.format))

    def __getattr__(self, name):
        d = vars(self)
        if d.has_key(name):
            return d[self]
        return getattr(self._img, name)

class TextureTool(object):


    parameters = (
        (gl.GL_TEXTURE_MAG_FILTER,   'GL_TEXTURE_MAG_FILTER'),
        (gl.GL_TEXTURE_MIN_FILTER,   'GL_TEXTURE_MIN_FILTER'),
        (gl.GL_TEXTURE_MIN_LOD,      'GL_TEXTURE_MIN_LOD'),
        (gl.GL_TEXTURE_MAX_LOD,      'GL_TEXTURE_MAX_LOD'),
        (gl.GL_TEXTURE_BASE_LEVEL,   'GL_TEXTURE_BASE_LEVEL'),
        (gl.GL_TEXTURE_MAX_LEVEL,    'GL_TEXTURE_MAX_LEVEL'),
        (gl.GL_TEXTURE_WRAP_S,       'GL_TEXTURE_WRAP_S'),
        (gl.GL_TEXTURE_WRAP_T,       'GL_TEXTURE_WRAP_T'),
        (gl.GL_TEXTURE_WRAP_R,       'GL_TEXTURE_WRAP_R'),
        (gl.GL_TEXTURE_BORDER_COLOR, 'GL_TEXTURE_BORDER_COLOR'),
        (gl.GL_TEXTURE_PRIORITY,     'GL_TEXTURE_PRIORITY'),
        (gl.GL_TEXTURE_RESIDENT,     'GL_TEXTURE_RESIDENT'),
        (gl.GL_TEXTURE_COMPARE_MODE, 'GL_TEXTURE_COMPARE_MODE'),
        (gl.GL_TEXTURE_COMPARE_FUNC, 'GL_TEXTURE_COMPARE_FUNC'),
        (gl.GL_DEPTH_TEXTURE_MODE,   'GL_DEPTH_TEXTURE_MODE'),
        (gl.GL_GENERATE_MIPMAP,      'GL_GENERATE_MIPMAP'))


    @classmethod 
    def current_parameters(cls, target=gl.GL_TEXTURE_2D):
        """Returns full listing of current texture parameters as list
        of 3-tuples consisting of (
        """
        listing = []
        for (param, name) in cls.parameters:
            v = gl.GLint()
            gl.glGetTexParameteriv(target, param, v)
            listing.append((param, name, v.value))
        return listing



