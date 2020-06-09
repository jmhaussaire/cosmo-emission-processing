from emiproc.grids import COSMOGrid, VPRMGrid
import os
import time

# inventory
inventory = 'VPRM'

# model either "cosmo-art" or "cosmo-ghg" (affect the output units)
model = 'cosmo-ghg'

# path to input inventory
#input_path = "/scratch/snx3000/haussaij/VPRM/20150701/gpp_2015070110.nc"
input_path = "/scratch/snx3000/haussaij/VPRM/input/vprm_fluxes_EU5km_20150701.nc"

# input grid
input_grid = VPRMGrid(
#    xmin=-30,
#    xmax=60,
#    ymin=30,
#    ymax=72,
    input_path,
    dx=5000,
    dy=5000,
    name='VPRM',
)

# input species
species = ["CO2_GPP_F", "CO2_RA_F"]

# input categories
categories = []

# mapping from input to output species (input is used for missing keys)
in2out_species = {}

# mapping from input to output species (input is used for missing keys)
# All the categories will be summed. 
# There is no mapping between these catgories and GNFR yet
in2out_category = {}

# output variables are written in the following format using species
varname_format = '{species}'


# Domain
# CHE_Europe domain
cosmo_grid = COSMOGrid(
    nx=764,
    ny=614,
    dx=0.05,
    dy=0.05,
    xmin=-17-0.1,
    ymin=-11-0.1,
    pollon=-170,
    pollat=43,
)


# output path and filename
output_path = os.path.join('outputs', 'VPRM')
output_name = "vprm.nc"

# resolution of shape file used for country mask
shpfile_resolution = "110m"

# number of processes computing the mapping inventory->COSMO-grid
nprocs = 2

# metadata added as global attributes to netCDF output file
nc_metadata = {
    "DESCRIPTION": "Gridded hourly fluxes",
    "DATAORIGIN": "VPRM",
    "CREATOR": "Jean-Matthieu Haussaire",
    "EMAIL": "jean-matthieu.haussaire@empa.ch",
    "AFFILIATION": "Empa Duebendorf, Switzerland",
    "DATE CREATED": time.ctime(time.time()),
}



