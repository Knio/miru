# -*- test-case-name: miru.test.test_controls -*-
# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details

import ctypes
import sys

from pyglet.gl import gl

import pyglet
from pyglet.window import key, mouse
from euclid import Vector3

from miru import imiru
from miru import utils
from miru import camera

from zope.interface import implements

from twisted.python import failure


class MouseControl(pyglet.event.EventDispatcher):

    implements(imiru.IDevice)


    # The context is intialized after a control is bound
    # to the context in the Context's initializer
    context = None

    _selected = None
    selectable = None
    accessible_button = mouse.LEFT
    accessible_modifiers = 0
    

    def __init__(self, accessible=False, sensitivity=0.5):
        self.focussed = None
        self.accessible = accessible
        self._orig_pos = Vector3(0, 0, 0)
        self._orig_angle = Vector3(0, 0, 0)
        self.mouse_state = _mouse_state
        self.sensitivity = sensitivity

    def enable(self, window=None):
        window = window or self.context.window
        window.push_handlers(self)
        window.push_handlers(self.mouse_state)
        return self

    def disable(self, window=None):
        window = window or self.context.window
        window.remove_handlers(self)
        window.remove_handlers(self.mouse_state)


    def on_mouse_motion(self, x, y, dx, dy):
        if self.accessible and self._selected:
            self.dispatch_event('on_drag', self._selected, x, y, dx, dy,
                    self.accessible_button, self.accessible_modifiers)


    def on_mouse_press(self, x, y, button, modifiers):
        if not self._selected:
            self._select(x, y, button, modifiers)


    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if not self.accessible and self._selected:
            self.dispatch_event('on_drag', self._selected, x, y, dx, dy,
                    button, modifiers)
        #self._move(x, y, dx, dy, button, modifiers, drag=(not self.accessible))

    def on_mouse_release(self, x, y, button, modifiers):
        if self._selected:
            try:
                self.dispatch_event('on_release', self._selected, x, y,
                        button, modifiers)
            except TypeError:
                pass
        if not self.accessible:
            utils.change_cursor(
                    self.context.window.CURSOR_DEFAULT,
                    self.context.window)
            self._selected = None


    def _select(self, x, y, button, modifiers):

        target = utils.select_object(x, y, self.selectable)

        if target:
            self._selected = target
            self.dispatch_event('on_select', target, x, y, button,
                    modifiers)
        elif self._selected:
            self.dispatch_event('on_release', self._selected, x, y, button,
                    modifiers)
            self._selected = None
        

    def on_select(self, target, x, y, button, modifiers):
        pass
    
    def on_release(self, target, x, y, button, modifiers):
        pass

    def on_drag(self, target, x, y, dx, dy, button, modifiers):
        pass

MouseControl.register_event_type('on_select')
MouseControl.register_event_type('on_drag')
MouseControl.register_event_type('on_release')

class SimpleMouseControl(MouseControl):
    """This is for demonstrations purposes only.
    """

    MODE_NOOP = 0
    MODE_TRANSLATE = 1
    MODE_ROTATE = 2
    
    AXIS_NONE = 0
    AXIS_X = 1
    AXIS_Y = 2
    AXIS_Z = 3

    mode = MODE_TRANSLATE
    axis = AXIS_NONE


    def on_select(self, target, x, y, button, modifiers):
        utils.change_cursor(
                self.context.window.CURSOR_HAND,
                self.context.window )

    def on_release(self, target, x, y, button, modifiers):
        utils.change_cursor(
                self.context.window.CURSOR_DEFAULT,
                self.context.window )
        self.mode = self.MODE_TRANSLATE

    def on_drag(self, target, x, y, dx, dy, button, modifiers):
        if self.mode == self.MODE_TRANSLATE:
            try:
                handler = imiru.ITranslationHandler(target)
            except TypeError:
                failure.Failure().printTraceback()
                return
            return handler(self, target, x, y, dx, dy)

        elif self.mode == self.MODE_ROTATE:
            try:
                handler = imiru.IRotationHandler(target)
            except TypeError:
                failure.Failure().printTraceback()
                return
            return handler(self, target, x, y, dx, dy)

    def on_key_press(self, symbol, modifiers):
        if self._selected is None:
            return
        #if self.mode == MouseControl.MODE_NOOP:
        start = False
        if symbol == key.G and self.mode in (self.MODE_NOOP, self.MODE_ROTATE):
            self.mode = self.MODE_TRANSLATE
            start = True
        elif symbol == key.R and self.mode in (
                self.MODE_NOOP, self.MODE_TRANSLATE):
            self.mode = self.MODE_ROTATE
            start = True

        if start:
            self._orig_pos = Vector3(*self._selected.pos)
            self._orig_angle = Vector3(*self._selected.angle)

        if self.mode != self.MODE_NOOP:
            if symbol == key.X:
                self.axis = (self.AXIS_X, self.AXIS_NONE)[
                                self.axis == self.AXIS_X]
            elif symbol == key.Y:
                self.axis = (self.AXIS_Y, self.AXIS_NONE)[
                                self.axis == self.AXIS_Y]
            elif symbol == key.Z:
                self.axis = (self.AXIS_Z, self.AXIS_NONE)[
                                self.axis == self.AXIS_Z]

    def on_mouse_scroll(self, x, y, dx, dy):
        self.context.camera.pos.z += (dy * self.sensitivity)
    
    def on_mouse_press(self, x, y, button, modifiers):

        # Middle mouse button allows us to manipulate 
        # the camera orientation
        if button == mouse.MIDDLE:
            self._selected = self.context.camera
            self.mode = self.MODE_ROTATE
            if modifiers & key.MOD_SHIFT:
                self.mode = self.MODE_TRANSLATE
            return 
        
        if not (self._selected and self.mode):
            return self._select(x, y, button, modifiers)

        if button == mouse.RIGHT:
            self._selected.pos = self._orig_pos
            self._selected.angle = self._orig_angle
        elif button == mouse.LEFT:
            self.mode = self.MODE_NOOP
            self.axis = self.AXIS_NONE
            utils.change_cursor(self.context.window.CURSOR_DEFAULT,
                    self.context.window)

class MouseStateHandler(object):

    x = 0
    y = 0

    def on_mouse_motion(self, x, y, dx, dy):
        self.x = x
        self.y = y

_mouse_state = MouseStateHandler()

def mouseXY():
    return _mouse_state.x, _mouse_state.y


