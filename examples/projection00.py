import itertools

from pyglet import font
from pyglet import clock
from pyglet.window import key

from miru import ui
from miru.context import context
from miru import utils
from miru import camera
from miru import input


class ProjectionWindow(ui.TestWindow):

    projections = itertools.cycle([camera.OrthographicProjection(),
        camera.PerspectiveProjection()])

    def on_key_press(self, symbol, modifiers):
        super(ProjectionWindow, self).on_key_press(symbol, modifiers)
        if symbol == key.P:
            proj = self.projections.next()
            print ' > changing projection to', proj
            context.camera.projection = proj


w = ProjectionWindow(680, 400)
w.set_vsync(False)

utils.addFpsDisplay(context)

context.window = w
for pos in ((1,1,-4),):
    o = w._load_object()
    o.pos = pos
context.control = input.SimpleMouseControl()

while not w.has_exit:
    clock.tick()
    w.clear()
    w.dispatch_events()
    context.render()
    w.flip()
w.close()




