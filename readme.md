# About

Python library for XrdPatterns including file import, file export and postprocessing functionalities.
The file import and export functionalities are built on C++ library  [xylib](https://github.com/wojdyr/xylib) so beyond a standard python install this library also requires:
- A C++ compiler and standard library
- A C++ to python bridge (Swig)

It allows for (lotsa things)


# Setup

## System level requirements
For Ubuntu 22.04:
```
sudo apt install build-essential	# GNU C++ compiler
sudo apt install libboost-all-dev       # C++ libraries provided by Boost
sudo apt install swig 			# python -> C++ bridge
```

For Windows >10 you may try the following in PowerShell (requires [Chocolatey](https://chocolatey.org/)):
```
choco install mingw  # MinGw 
choco install swig
```
## Python library
Once the system level requirements are installed, the library can be installed using pip:
```
pip install xrdpattern
```
