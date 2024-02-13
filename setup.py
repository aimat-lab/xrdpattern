import os

from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

requirements += [f"xylib-py @ file://localhost/{os.getcwd()}/xylib"]

setup(
    name='xrd_pattern',
    version='0.2.0',
    packages=['xrd_pattern'],
    install_requires=requirements
)
