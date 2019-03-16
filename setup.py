#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Setup script for aggdraw
#
# Usage:
#
#   To build in current directory:
#   $ python setup.py build_ext -i
#
#   To build and install:
#   $ python setup.py install
#
from __future__ import print_function
import os
import sys
import subprocess
import platform
from distutils.sysconfig import get_config_var
from distutils.version import LooseVersion

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

VERSION = "1.3.10"

SUMMARY = "High quality drawing interface for PIL."

DESCRIPTION = """\

The aggdraw module implements the basic WCK 2D Drawing Interface on
top of the AGG library. This library provides high-quality drawing,
with anti-aliasing and alpha compositing, while being fully compatible
with the WCK renderer.

"""


def is_platform_mac():
    return sys.platform == 'darwin'


# For mac, ensure extensions are built for macos 10.9 when compiling on a
# 10.9 system or above, overriding distuitls behaviour which is to target
# the version that python was built for. This may be overridden by setting
# MACOSX_DEPLOYMENT_TARGET before calling setup.py
if is_platform_mac():
    if 'MACOSX_DEPLOYMENT_TARGET' not in os.environ:
        current_system = LooseVersion(platform.mac_ver()[0])
        python_target = LooseVersion(get_config_var('MACOSX_DEPLOYMENT_TARGET'))
        if python_target < '10.9' and current_system >= '10.9':
            os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.9'


def _get_freetype_config():
    print("Trying freetype-config to find freetype library...")
    try:
        # pointer to freetype build directory (tweak as necessary)
        return subprocess.check_output(
            ['freetype-config', '--prefix']).strip().replace(
            b'"', b'').decode()
    except (OSError, subprocess.CalledProcessError):
        return None


def _get_freetype_with_ctypes():
    print("Using ctypes to find freetype library...")
    from ctypes.util import find_library
    ft_lib_path = find_library('freetype')
    if ft_lib_path is None:
        return None

    if not sys.platform.startswith('linux') and \
            not os.path.isfile(ft_lib_path):
        return None
    elif not os.path.isfile(ft_lib_path):
        # try prefix since find_library doesn't give a full path on linux
        for bdir in (sys.prefix, '/usr', '/usr/local'):
            lib_path = os.path.join(bdir, 'lib', ft_lib_path)
            if os.path.isfile(lib_path):
                return bdir
        else:
            # freetype is somewhere on the system, but we don't know where
            return None
    ft_lib_path = os.path.dirname(ft_lib_path)
    lib_path = os.path.realpath(os.path.join(ft_lib_path, '..'))
    return lib_path


def _get_freetype_with_pkgconfig():
    print("Trying 'pkgconfig' to find freetype library...")
    try:
        import pkgconfig
        return pkgconfig.variables('freetype2')['prefix']
    except (ImportError, KeyError, ValueError):
        return None


FREETYPE_ROOT = os.getenv('AGGDRAW_FREETYPE_ROOT')
for func in (_get_freetype_config, _get_freetype_with_ctypes,
             _get_freetype_with_pkgconfig):
    if FREETYPE_ROOT is None:
        FREETYPE_ROOT = func()

if FREETYPE_ROOT is None:
    print("=== freetype not available")
else:
    print("=== freetype found: '{}'".format(FREETYPE_ROOT))

sources = [
    # Reference all of svg. It's small enough so there is no reason
    # to try to cherry pick sources.
    './agg/src/agg_arc.cpp',
    './agg/src/agg_arrowhead.cpp',
    './agg/src/agg_bezier_arc.cpp',
    './agg/src/agg_bspline.cpp',
    './agg/src/agg_color_rgba.cpp',
    './agg/src/agg_curves.cpp',
    './agg/src/agg_embedded_raster_fonts.cpp',
    './agg/src/agg_gsv_text.cpp',
    './agg/src/agg_image_filters.cpp',
    './agg/src/agg_line_aa_basics.cpp',
    './agg/src/agg_line_profile_aa.cpp',
    './agg/src/agg_rounded_rect.cpp',
    './agg/src/agg_sqrt_tables.cpp',
    './agg/src/agg_trans_affine.cpp',
    './agg/src/agg_trans_double_path.cpp',
    './agg/src/agg_trans_single_path.cpp',
    './agg/src/agg_trans_warp_magnifier.cpp',
    './agg/src/agg_vcgen_bspline.cpp',
    './agg/src/agg_vcgen_contour.cpp',
    './agg/src/agg_vcgen_dash.cpp',
    './agg/src/agg_vcgen_markers_term.cpp',
    './agg/src/agg_vcgen_smooth_poly1.cpp',
    './agg/src/agg_vcgen_stroke.cpp',
    './agg/src/agg_vpgen_clip_polygon.cpp',
    './agg/src/agg_vpgen_clip_polyline.cpp',
    './agg/src/agg_vpgen_segmentator.cpp',
    './agg-svg/agg_svg_gradient.cpp',
    './agg-svg/agg_svg_parser.cpp',
    './agg-svg/agg_svg_path_renderer.cpp',
    './agg-svg/agg_svg_path_tokenizer.cpp',
    './expat/loadlibrary.c',
    './expat/xmlparse.c',
    './expat/xmlrole.c',
    './expat/xmltok.c',
    './expat/xmltok_impl.c',
    './expat/xmltok_ns.c',
    ]

# define VERSION macro in C++ code, need to quote it
defines = [('VERSION', VERSION)]

include_dirs = ["agg/include",
                'agg-svg',
                'expat']
library_dirs = []

libraries = []

if FREETYPE_ROOT:
    defines.append(("HAVE_FREETYPE2", None))
    sources.extend([
        "agg/font_freetype/agg_font_freetype.cpp",
        ])
    include_dirs.append("agg/font_freetype")
    include_dirs.append(os.path.join(FREETYPE_ROOT, "include"))
    include_dirs.append(os.path.join(FREETYPE_ROOT, "include/freetype"))
    include_dirs.append(os.path.join(FREETYPE_ROOT, "include/freetype2"))
    library_dirs.append(os.path.join(FREETYPE_ROOT, "lib"))
    libraries.append("freetype")

if sys.platform == "win32":
    libraries.extend(["kernel32", "user32", "gdi32"])
    defines.append(("NOMINMAX", None))

setup(
    name="aggdraw",
    version=VERSION,
    author="Fredrik Lundh",
    author_email="fredrik@pythonware.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Topic :: Multimedia :: Graphics",
        ],
    description=SUMMARY,
    download_url="http://www.effbot.org/downloads#aggdraw",
    license="Python (MIT style)",
    long_description=DESCRIPTION.strip(),
    platforms="Python 2.7 and later.",
    url="https://github.com/pytroll/aggdraw",
    ext_modules=[
        Extension("aggdraw", ["aggdraw.cxx"] + sources,
                  define_macros=defines,
                  include_dirs=include_dirs,
                  library_dirs=library_dirs, libraries=libraries
                  )
        ],
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    tests_require=['pillow', 'pytest'],
    )
