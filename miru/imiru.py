# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details


from zope.interface import Interface, Attribute

class IObject(Interface):
    """An object that can be moved around, etc.
    """

#class IWorldObject(Interface):
#    """A object rendered in 3D space (the camera render context).
#    """

class IEnvironment(Interface):
    window = Attribute("""
        The current window (C{pyglet.window.Window})""")

    objects = Attribute("""
        C{list} of objects in the world (current scene)""")

    osd = Attribute("""
        (Optional) On Screen Display (miru.osd.OSD)""")

    cameras = Attribute("""
        Map of cameras set up for the scene.  If not explicitly set,
        the current camera is assigned the key `main'""")

    camera = Attribute("""
        The current camera used for rendering the scene""")

    handle = Attribute("""
        (Optional) Mouse handler for selecting objects""")


    currentRenderStage = Attribute("""
        The current render stage being rendered by the environment
        or None if the environment is not currently rendering.
        """)

    renderStages = Attribute("""
        C{list} of C{IRenderStage} set on environment in order.
        """)

    # TODO - consider property globalDriverState to make this
    # easily customizable

    def renderStage(iface):
        """Get the C{IRenderStage} provider for the given Interface.

        @param iface: The C{IRenderStage} Interface we are looking for
        """

    def setRenderStages(*ifaces):
        """Set render stages for the environment.  The interfaces supplied must
        first have a provider utility registered with
        C{miru.components.registerUtility} before calling this method.

        @param iface: Listing of C{IRenderStage} Interfaces.
        """

    def render():
        """Render the evironment - invoking its render stages in the order added.
        """

    def addobj(obj):
        """Add an object to the environment.
        """

    def delobj(obj):
        """Remove an object from the environment.
        """

class IRuntime(Interface):
    """The main loop for the game
    """
    def run():
        """Run the game
        """

class IPositional(Interface):
    """An object with position and orientation in space
    """
    pos = Attribute("""
            Vector3 instance giving location of object in space""")

    angle = Attribute("""
            Vector3 instance giving the orientation of the object""")
    
    scale = Attribute("""
            Vector3 instance giving the scale of the object""")


class IConstraint(Interface):
    """A constraint on a position or angle vector.
    """

    def constrain(vector):
        """Get the constrained vector.
        """

class ILineEditorMode(Interface):
    """Line editor mode ... possible examples:
    Python, Shell, Text 
    """

    def on_line(line):
        """Read a line and return output or None
        """

    def on_key_press(symbol, modifiers):
        """Callback for key entry.  Return value is ignored.
        """

    def on_text(text):
        """Callback for text entry.  Return value is ignored.
        """


class IDevice(Interface):
    target = Attribute("""
        IPositional provider which is subject to
        transformation by the device.  Transformation depends on mode.""")

    mode = Attribute("""
        The current transformation mode (TR_ROTATE,
        TR_TRANSLATE)""")

    TR_TRANSLATE = Attribute("""
        Constant for translation mode.""")

    TR_ROTATE = Attribute("""
        Constant for rotation mode.""")

    TR_NOOP = Attribute("""
        Noop => Non-transformation mode.""")

    def on_select(self, target, button, modifiers, x, y):
        """Callback for selection of objects in Scene.
        """

class ICamera(Interface):
    
    projection = Attribute("""
        The C{IProjection} for the camera.
        """)

    lights = Attribute("""
        The lights groups used for lighting by the camera""")

    def render(select_pass=0, effect_pass=0, visible=None, lights=None,
            before_render=None):
        """Render camera scene.
        """


class ILight(Interface):
    def on():
        """Turn light on
        """

class ILightGroup(Interface):
    """A set of lights.  Lights should be attached to camera instance
    since on render the light group will be switched on and off.  Most
    OpenGL implementations will support up to 8 lights.
    """
    def on():
        """Turn light group on
        """

    def off():
        """Turn light group off
        """


class IProjection(Interface):

    clear_color = Attribute("""
        Background color (4-tuple of C{float}) of projection
        """)

    camera = Attribute("""
        C{ICamera} the projection is attached""")

    def on_resize(width, height, x=0, y=0):
        """resize handler for the projection.

        @param width: the current width of the window

        @param height: the current height of the window

        @param x: optional left edge of viewport

        @param y: optional bottom edge of viewport
        """

class IDrawable(Interface):
    """Something that can be drawn to the screen.
    """
    def draw():
        """Draw the object 
        """

# Rather than DebuggingDrawable and other stupid shit like
# that, we should have generic render stages into which objects
# can be plugged.

class IDebuggingDrawable(IDrawable):
    pass


class IMesh(IDrawable):
    pass

class IBlittable(Interface):
    def blit(x, y):
        """Blit the object at x,y
        """


class ITrack(Interface):
    """Defines a tracking relationship between two objects - one tracking
    changes on the position or angle of the other.
    """
    tracker = Attribute("""
        The tracking object""")

    tracked = Attribute("""
        The tracked object""")

    def __call__(tracked, vector, delta):
        """Callback on changes to the tracked object.
        """

    def untrack():
        """Destroy this track - unregistering self as a positional tracker on tracked
        """

class IDraggable(Interface):
    pass

class IEffect(Interface):

    def enable():
        """Enable the effect
        """

    def disable():
        """Disable the effect
        """

class ITranslationHandler(Interface):

    def __call__(control, target, x, y, dx, dy):
        """Handler for translation

        @param control: The controller

        @param target: The object to translate

        @param x: current x location of mouse in screen coordinates

        @param y: current y location of mouse in screen coordinates

        @param dx: difference in x from last location

        @param dy: difference in y from last location
        """

class IRotationHandler(Interface):

    def __call__(handle, x, y, dx, dy):
        """Handler for rotation

        @param control: The control

        @param target: The target to rotate

        @param x: current x location of mouse in screen coordinates

        @param y: current y location of mouse in screen coordinates

        @param dx: difference in x from last location

        @param dy: difference in y from last location
        """


class IPressable(Interface):
    """An object that can be pressed by a device.
    """
    def on_device_press(device, x, y, button, modifiers):
        """Callback for device clicking in widget region.

        @param x: x location of device

        @param y: y location of device

        @param button: the button number (0,1,2..)

        @param modifiers: keyboard modifiers
        """

class IReleasable(Interface):
    """An object that can be clicked by a device.
    """
    def on_device_release(device, x, y, button, modifiers):
        """Callback for device released in widget region.

        @param x: x location of device

        @param y: y location of device

        @param button: the button number (0,1,2..)

        @param modifiers: keyboard modifiers
        """

class IEnterable(Interface):
    """An object that can be entered by a device.
    """
    def on_device_enter(device, x, y):
        """Callback for device entering widget region

        @param device: The device entering

        @type  device: C{IDevice}

        @param x: x coordinate of device

        @param y: y coordinate of device
        """

class IExitable(Interface):
    """An object that can be exited by a device.
    """
    def on_device_exit(device, x, y):
        """Callback for device exiting widget region

        @param device: The device entering

        @type  device: C{IDevice}

        @param x: x coordinate of device

        @param y: y coordinate of device
        """

class IHoverable(IEnterable, IExitable):
    """Objects that are hoverable will receive hover events whenever
    the mouse is moved after entering the objects region. An object
    must be enterable an exitable to be hoverable.
    """
    def on_device_hover(device, x, y, dx, dy):
        """Propagate hover event to the object.

        @param device: the hovering device

        @type device: C{IDevice}

        @param x: the x coordinate of the device on hover

        @param y: the y coordinate of the device on hover

        @param dx: difference between last x position of device

        @param dy: difference between last y position of device
        """


class IWidget(IPressable, IReleasable, IHoverable):
    """UI Widget responding to all device events.
    """

class IRenderStage(Interface):

    objects = Attribute("""
        Object that belong to the render stage.
        """)

    def render():
        """Do the rendering.
        """

    def addobj(obj):
        """And a drawable object to this C{IRenderStage}.

        @param obj: The object to add C{IDrawable}
        """
    
    def delobj(obj):
        """Remove a drawable object to this C{IRenderStage}.

        @param obj: The object to add C{IDrawable}
        """

class IWorldRenderStage(IRenderStage):
    """Render stage for objects in world coordinates.
    """

class IOSDRenderStage(IRenderStage):
    """Render stage for objects in our on screen display.
    """

class IDebuggingRenderStage(IRenderStage):
    """Debugging render stage - objects drawn without lighting.
    """

class IBlittableRenderStage(IRenderStage):
    """Render blittable objects - objects should be maintained in order of 
    z-position
    """

class IShaderRenderStage(IRenderStage):
    """Render stage for GLSL
    """


class IImage(IDrawable):

    anchor_x = Attribute("""
        x anchor for drawing image""")

    anchor_y = Attribute("""
        y anchor for drawing image""")

    width = Attribute("""
        The image width""")

    height = Attribute("""
        The image height""")

    scale = Attribute("""
        The scale of the image (default 0.1)
        """)

