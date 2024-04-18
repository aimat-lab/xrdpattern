## About

Python library for handling XrdPatterns including support for importing from data files, exporting as json file, visualization and postprocessing.
The data file import functionalities are largely built on the C++ library  [xylib](https://github.com/wojdyr/xylib) so beyond a standard python install this library also requires:
- A C++ compiler and standard library
- A C++ to python bridge (Swig)

Loading Diffractogram patterns from the following data formats is supported:
- Siemens/Bruker RAW ver. 1/2/3/4 (.raw)
- Stoe RAW (.raw) (! In progress)
- Comma seperated values (.csv) (! In progress)
- Plain text tab seperated values (.txt) (! In progress)
- Crystallographic Information File for Powder Diffraction (.cif)
- Siemens/Bruker UXD (.uxd)
- Philips UDF (.udf)
- Freiberg Instruments XSYG (.xysg)
- Philips RD ver. 3/5 (.rd)
- PANalytical XRDML (.xrdml)
- Rigaku DAT (.dat)
- Sietronics Sieray CPI (.cpi)
- XFIT/Koalariet XDD (.xdd)
- RIET7 DAT (.dat)
- DBWS/DMPLOT data file (.dbw, .rit, .neu)
- Canberra CNF (.cnf)
- Canberra AccuSpec MCA (.mca)
- χPLOT CHI (.chi)
- Bruker SPC (.spc)
- XrdPattern json (.json)

## Setup

### System level requirements
For Ubuntu 22.04:
```
sudo apt install build-essential	# GNU C++ compiler
sudo apt install libboost-all-dev       # C++ libraries provided by Boost
sudo apt install swig 			# python -> C++ bridge
```

For Windows >10 you may try the following in PowerShell (requires [Chocolatey](https://chocolatey.org/)):
```
choco install mingw  # C++ compiler and std library
choco install swig   # python -> C++ bridge
```
### Python library
Once the system level requirements are installed, the library can be installed using pip:
```
pip install xrdpattern
```
