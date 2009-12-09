#!/usr/bin/env python

# Try to use setuptools from http://peak.telecommunity.com/DevCenter/setuptools
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.core import Extension
try:
    from Pyrex.Distutils import build_ext
except ImportError:
    build_ext = None

VERSION = '0.1.0'
BUILD_C_EXTS = False

extensions = []
cmdclass = {}
if BUILD_C_EXTS and build_ext:
    particles_extension = Extension('ext.particles',
            [os.path.join('miru', 'ext', 'particles.pyx')])
    extensions = [particles_extension]
    cmdclass = { 'build_ext' : build_ext}
if BUILD_C_EXTS and not build_ext:
    from warnings import warn
    warn("Pyrex is required to build C-based modules in miru.\n"
         "Get Pyrex at: http://www.cosc.canterbury.ac.nz/greg.ewing/python/Pyrex/")

setup(
    author='Drew Smathers',
    author_email='drew dot smathers at gmail dot com',
    name='Miru',
    version=VERSION,
    install_requires=['zope.interface','pyglet','Twisted==8.2.0'],
    description="""Higher-level graphics abstractions for pyglet""",
    license='MIT License',
    url='http://enterthefoo.com:8001/Miru',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Graphics :: 3D Rendering'],
    packages=[ 'miru', 'miru.tools', 'miru.test' ],
    py_modules=[ 'euclid' ],
    package_dir={'miru': 'miru'},
    package_data={'miru': ['test/*.obj', 'test/*.mtl']},
    ext_package='miru',
    ext_modules = extensions,
    cmdclass = cmdclass
    )
