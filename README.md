# Online emission processing

Preprocessing of the emissions for the online emission module of cosmo.
Produces gridded annual emissions as well as temporal and vertical profiles.

## Installation
To use the code, just download or clone the repository. The code does not need to be
installed, but it has the following requirements on third-party packages:

* Python (>= 3.6)
* cartopy
* netCDF4
* numpy
* shapely

Please note emission inventories are not included in the repository, but have to
be obtained separately.

## Quickstart

1. Take one of the configuration files and adjust it to your case.

2. Generate the emission files:
```
    $ python main_{tno|ch}_example.py config_{tno|ch}.py
```

3. Generate the profiles:
```
    $ python profiles/temporal_profiles_example.py
    $ python profiles/vertical_profiles_example.py
```

## Gridded annual emissions

Emissions are read from the inventory inventory and projected onto the COSMO grid.

The necessary information, such as grid characterstics and species, are supplied via
a config file. Since emission inventories can be structured quite differently, it may
also be necessary to adapt the main script. The provided examples are a good starting
point.

### Grids

In the file `grids.py` you can find definitions for classes handling common gridtypes
(COSMO, TNO, swiss). Use them in your configuration file to specify your grid.

If your grid can not be represented by an existing one, implement your own grid class
by inheriting from the `Grid` baseclass and implementing the required methods.

## Temporal and vertical profiles

The temporal and vertical profiles are generated by the scripts in the `profiles/`
directory.

## Notice

This repository is a merge of

https://gitlab.empa.ch/abt503/users/hjm/online-emission-processing

https://gitlab.empa.ch/abt503/users/jae/online-emission-processing

https://gitlab.empa.ch/abt503/users/muq/online_emission_cosmoart

and will be hosted at

https://github.com/C2SM-RCM/cosmo-emission-processing.

It deliberately is not a fork of any of the existing repositories since that would introduce an
unwanted dependency. However, the commit history will be kept intact as much as possible.

## Formatting

This code is formatted using [black](https://black.readthedocs.io/en/stable/).
Run `find . -name '*.py' -exec black -l 80 --target-version py36 {} +` before commiting
to reformat the files.

## License

This work is licensed under the Creative Commons Attribution 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
