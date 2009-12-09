import os
import sys

from twisted.internet import utils, defer

from miru.test import reportFtest


BASE = os.path.dirname(__file__)

# Add tests here ass 2-tuple consiting of the test
# script name (with no .py extension) and the description
# of user expectations.

TESTS = (
      
    ('projection00',
     '''
     You should see an on object in perspective projection.
     Press P and the view will change to an orthographic
     projection.
     '''),
    #('debug00',
    # '''
    # You should see a checker-patterned sphere and a cube.
    # '''),
    #('debug01',
    # '''
    # You should see a checker-patterned sphere and a yellow
    # coordinate plane.
    # '''),
    ('shader00',
     '''
     You should see 4 spheres with plastic-like shading.
     '''),
    ('track00',
     '''
     You should see an object move from right to left
     with the camera tracking it by rotating its line
     of vision.
     '''),
    ('track01',
     '''
     The camera should be looking down at the moving object
     and following it as it oscillates left to right.
     The camera does not change its position.
     '''),
    ('track02',
     '''
     The camera should follow the object at the center of 
     the screen along the x, y and z axes.
     '''),
    ('track03',
     '''
     The camera should follow the object only as it approaches
     the edge of the window.  The object does not get further
     from the camera on the z-axis (as it moves further into the
     screen).
     '''),
    ('toon01',
     '''
     You should see a green torus toon shaded.
     '''),
    ('toon02',
     '''
     You should see 4 differently colored tori
     rotating around a common pivot.
     '''),
    ('toon03',
     '''
     You should see 4 differently colored tori
     inside a rotating box.  The box faces should disappear
     an reappear to remain visible only when they are not
     occluding th tori.
     '''),
    ('effects00',
     '''
     You should see 3 objects with their
     reflection on the plane beneath them.
     '''),
    ('effects01',
     '''
     You should see some objects in fog.
     '''),
    ('effects02',
     '''
     You should see some objects in fog and reflections 
     below them.
     '''),
    ('lights00',
     '''
     You should see a small grid of objects with some
     colored lights over it.  You should be able to click
     on the bulb of a light to move it around.  The white
     light is a spotlight which remains focussed on the
     object floating above the grid.
     '''),
    ('viewports00',
     '''
     You should see 4 viewports dividing the window evenly 
     with different projections on the same scene containing
     3 objects.
     '''),
    ('mesh01',
     '''
     You should see a large swarm of textured objects rotating
     around a common point.
     '''),
    ('mesh02',
     '''
     You should see serveral textured objects rotating around a
     common point and with the texture projected onto them
     from the vantage point.
     '''),
    ('mesh03',
     '''
     You should see a single textured object with its texture moving.
     '''),
    ('mesh05',
     '''
     You several different meshes all textured with the same
     projective texture.
     '''),
    ('cubemap02',
     '''
     You should see a cube-mapped yam spinning in place.
     '''),
    ('pointsprite01',
     '''
     You should see a simple particle animation - points moving
     away from a cetral point in random directions.
     '''),


)


tests = sys.argv[1:]

@defer.inlineCallbacks
def run():
    env = dict(os.environ)
    for (test, description) in TESTS:
        if tests and test not in tests:
            continue
        print description
        script = os.path.join(BASE, test + '.py')
        yield utils.getProcessValue('python', [script], env)
        result = raw_input("Did it work? [y/N] ")
        reportFtest(test, result)
    reactor.stop()

from twisted.internet import reactor
reactor.callWhenRunning(run)
reactor.run()

