## About

Python library for handling XrdPatterns including support for importing from data files, exporting as json file, visualization and postprocessing.
The data file import functionalities are largely built on the C++ library  [xylib](https://github.com/wojdyr/xylib) so beyond a standard python install this library also requires:
- A C++ compiler and standard library
- A C++ to python bridge (Swig)

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


## Supported formats

Loading Diffractogram patterns from the following data formats is supported:

- Plain Text Files
    - Comma seperated values (.csv)
    - Crystallographic Information File for Powder Diffraction (.cif)
    - Custom XrdPattern json format (.json)
    - Plain text tab seperated values (.txt) (! In progress)
    - PANalytical XRDML (.xrdml)
    - Freiberg Instruments XSYG (.xysg)

- Binaries:
  - Siemens/Bruker RAW ver. 1/2/3/4 (.raw)
  - Stoe RAW (.raw) (! In progress)
  - Siemens/Bruker UXD (.uxd)
  - Philips UDF (.udf)
  - Philips RD ver. 3/5 (.rd)
  - Rigaku DAT (.dat)
  - RIET7 DAT (.dat)
  - Sietronics Sieray CPI (.cpi)
  - XFIT/Koalariet XDD (.xdd)
  - DBWS/DMPLOT data file (.dbw, .rit, .neu)
  - Canberra CNF (.cnf)
  - Canberra AccuSpec MCA (.mca)
  - χPLOT CHI (.chi)
  - Bruker SPC (.spc)

When using Xrdpattern.load(fpath=xrdfile.suffix), the format will be automatically determined from the suffix unless
there are are several formats with this format as with .raw and .dat. 
In this case the format will need to be manually specified.