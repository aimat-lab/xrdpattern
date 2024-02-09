import os

from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

requirements += [f"xylib-py @ file://localhost/{os.getcwd()}/xylib"]

setup(
    name='xrdpattern',
    version='0.2.0',
    packages=['xrdpattern'],
    install_requires=requirements
)
