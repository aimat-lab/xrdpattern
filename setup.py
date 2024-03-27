#!/usr/bin/env python
from glob import glob

from setuptools import setup, find_packages, Extension
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

sources = [f for f in glob('xylib/*.cpp') if f != 'xylib_wrap.cpp'] + ['xylib.i']

with open('requirements.txt','r') as f:
    reqs = f.read().split('\n')

swig_opts = ['-c++', '-modern', '-modernargs']
if sys.version_info[0] == 3:
    swig_opts += ['-py3']

# noinspection PyTypeChecker
setup(name='xrdpattern',
      version='0.1.0',
      description='Python library for XrdPatterns including file import, file export and postprocessing functionalities',
      install_requires=reqs,
      long_description=("Python library for XrdPatterns including import from data files, "
                        "export as json file and postprocessing functionalities. The data file "
                        "import functionalities are built on C++ library xylib so beyond a standard "
                        "python install, this library also requires: "
                        "\n- A C++ compiler and standard library "
                        "\n- A C++ to python bridge (Swig)"),
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
