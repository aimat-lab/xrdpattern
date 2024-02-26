#!/usr/bin/env python

# This setup.py builds xylib as a python extension, which is experimental.
# The normal way of building xylib is using configure && make. Or cmake.
long_description="""\
xylib is a library for reading obscure file formats with data from
powder diffraction, spectroscopy and other experimental methods.
For the list of supported formats see https://github.com/wojdyr/xylib .

This module includes bindings to xylib and xylib itself.
The first two numbers in the version are the version of included xylib.

Prerequisites for building: SWIG and Boost libraries (headers only).
"""
from distutils.core import Extension
from glob import glob


from setuptools import setup, find_packages
import subprocess
import sys


# as per http://stackoverflow.com/a/21236111/104453
from distutils.command.build import build
class CustomBuild(build):

    def run(self):
        def check_package_installed(package_name):
            try:
                subprocess.check_output(['dpkg', '-s', package_name], stderr=subprocess.STDOUT)
                return True
            except subprocess.CalledProcessError:
                return False

        try:
            build.run(self)
        except Exception as e:
            print(f'\nERROR: An error occurred during the build process: \"{e}\"')
            required_packages = ['build-essential', 'libboost-all-dev', 'swig']
            missing_packages = [pkg for pkg in required_packages if not check_package_installed(pkg)]

            msg_pkg_str = ''
            for pkg in missing_packages:
                msg_pkg_str += f" - {pkg}\n"

            if msg_pkg_str:
                print("NOTE: This package requires a C++ compiler and a python to C++ bridge called \"swig\", make sure they are installed. \n"
                          "On Debian/Ubutu you may try installing the following packages via sudo apt install [package]:\n"
                          f"{msg_pkg_str}")
            sys.exit(1)


    sub_commands = [('build_ext', build.has_ext_modules),
                    ('build_py', build.has_pure_modules),
                    ('build_clib', build.has_c_libraries),
                    ('build_scripts', build.has_scripts)]

sources = glob('xylib/*.cpp') + ['xylib.i']

with open('requirements.txt','r') as f:
    reqs = f.read().split('\n')

swig_opts = ['-c++', '-modern', '-modernargs']
if sys.version_info[0] == 3:
    swig_opts += ['-py3']

setup(name='xrdpattern',
      version='1.6.3',
      description='Python bindings to xylib including a fix for RawV4 files. Xylib is written by Marcin Wojdyr (wojdyr@gmail.com). This package'
                  'includes a fix for RawV4 files that is necessary as a depdency for package xrdpattern',
      install_requires=reqs,
      long_description=long_description,
      packages=find_packages(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Scientific/Engineering :: Chemistry',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      author = 'Daniel Hollarek',
      author_email = 'daniel.hollarek@googlemail.com',
      license='LGPL2.1',
      url='https://github.com/aimat-lab/xrdpattern',
      ext_modules=[Extension('_xylib',
                             sources=sources,
                             language='c++',
                             swig_opts=swig_opts,
                             include_dirs=['.'],
                             libraries=[])],
      py_modules=['xylib'],
      cmdclass={'build': CustomBuild})
