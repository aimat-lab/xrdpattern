from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='xrdpattern',
    version='0.7.1',
    author='Daniel Hollarek',
    author_email='daniel.hollarek@googlemail.com',
    description='Python library for XrdPatterns including file import, file export, plotting and postprocessing functionalities',
    url='https://github.com/aimat-lab/xrdpattern',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=requirements
)
