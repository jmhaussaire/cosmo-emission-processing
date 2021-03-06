#! /usr/bin/env python

import argparse
import os
import xarray

import numpy as np

import emiproc
import emiproc.grids
import emiproc.misc

from emiproc.profiles import temporal_profiles as tp
from emiproc.profiles import vertical_profiles as vp
from emiproc import utilities as util

from emiproc.merge_inventories import merge_inventories
from emiproc import append_inventories
from emiproc import merge_profiles
from emiproc import hourly_emissions


DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'files')


def parse_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument(dest='task',
                        help='name of task')

    parser.add_argument('-c', '--case', dest='case', default=None,
                        help='name of case')

    parser.add_argument('-cf', '--case-file', dest='case_file', default=None,
                        help='path to case file')

    parser.add_argument('--output-path', dest='output_path', default='.',
                        help='name of output path')

    parser.add_argument('--nomenclature', dest='nomenclature', default='GNFR',
                        help='GNFR or SNAP', choices=['GNFR', 'SNAP'])

    parser.add_argument('--offline', dest='offline', action='store_true',
                        help='')

    parser.add_argument('--input-filename', dest='input_filename',
                        help='name of input filename')

    parser.add_argument('--output-filename', dest='output_filename',
                        help='name of output filename')

    args = parser.parse_args()

    return args



def main():

    args = parse_arguments()

    # make output path
    os.makedirs(args.output_path, exist_ok=True)

    if args.case is not None:
        cfg_path = os.path.join(os.path.dirname(__file__), '..', 'cases',
                                args.case)
        cfg = util.load_cfg(cfg_path)

    elif args.case_file is not None:
        cfg_path = args.case_file
        cfg = util.load_cfg(cfg_path)

    else:
        cfg = None

    if args.offline:
        if hasattr(cfg, 'cosmo_grid'):
            print('Add two-cell boundary on COSMO grid')
            cfg.cosmo_grid = emiproc.grids.COSMOGrid(
                nx = cfg.cosmo_grid.nx + 4,
                ny = cfg.cosmo_grid.ny + 4,
                dx = cfg.cosmo_grid.dx,
                dy = cfg.cosmo_grid.dy,
                xmin = cfg.cosmo_grid.xmin - 2 * cfg.cosmo_grid.dx,
                ymin = cfg.cosmo_grid.ymin - 2 * cfg.cosmo_grid.dy,
                pollon=cfg.cosmo_grid.pollon,
                pollat=cfg.cosmo_grid.pollat,
            )

        if hasattr(cfg, 'output_path'):
            cfg.output_path = cfg.output_path.format(online='offline')
    else:
        if hasattr(cfg, 'output_path'):
            cfg.output_path = cfg.output_path.format(online='online')

    if hasattr(cfg, 'output_path'):
        print('Output path: "%s"' % cfg.output_path)

    if args.task in ['grid']:

        if cfg is None:
            raise RuntimeError("Please supply a config file.")

        emiproc.main(cfg)


    elif args.task in ['merge']:

        if cfg is None:
            raise RuntimeError("Please supply a config file.")

        if args.offline:
            name = 'offline'
        else:
            name = 'online'

        base_inv = cfg.base_inv.format(online=name)
        nested_invs = dict((k.format(online=name), v) for k,v in
                            cfg.nested_invs.items())

        merge_inventories(base_inv, nested_invs,
                          cfg.output_path.format(online=name))

    elif args.task in ['tp-merge']:

        if cfg is None:
            raise RuntimeError("Please supply a config file.")

        merge_profiles.main(cfg.inv1, cfg.inv2, cfg.countries,
                            cfg.profile_path_in, cfg.profile_path_out)

    elif args.task in ['append']:

        if cfg is None:
            raise RuntimeError("Please supply a config file.")

        if args.offline:
            cfg.inv_1 = cfg.inv_1.format(online='offline')
            cfg.inv_2 = cfg.inv_2.format(online='offline')
            cfg.inv_out = cfg.inv_out.format(online='offline')
        else:
            cfg.inv_1 = cfg.inv_1.format(online='online')
            cfg.inv_2 = cfg.inv_2.format(online='online')
            cfg.inv_out = cfg.inv_out.format(online='online')

        append_inventories.main(cfg)


    elif args.task in ['vp']:

        profile_filename = os.path.join(DATA_PATH, 'vertical_profiles',
                                        'vert_prof_che_%s.dat' %
                                        args.nomenclature.lower())

        output_filename = os.path.join(args.output_path,
                                       'vertical_profiles.nc')

        vp.main(output_filename, profile_filename, prefix='%s_' %
                args.nomenclature)

    elif args.task in ['tp']: # temporal profiles

        if cfg is None:
            raise RuntimeError("Please supply a config file.")

        if cfg.profile_depends_on_species:
            tp.main_complex(cfg)
        else:
            tp.main_simple(cfg)


    elif args.task in ['hourly']:

        if cfg is None:
            raise RuntimeError("Please supply a config file.")

        # create hourly (offline) emissions
        hourly_emissions.main(
            path_emi=cfg.path_emi.format(online='offline' if args.offline else
                                         'online'),
            output_path=cfg.output_path.format(online='offline' if args.offline
                                               else 'online'),
            output_name=cfg.output_name,
            prof_path=cfg.prof_path,
            start_date=cfg.start_date,
            end_date=cfg.end_date,
            var_list=cfg.var_list,
            catlist=cfg.catlist,
            tplist=cfg.tplist,
            vplist=cfg.vplist,
            contribution_list=cfg.contribution_list,
            model=cfg.model
        )

    elif args.task in ['off2on']:
        input_filename = args.input_filename
        output_filename = args.output_filename

        # open file and cut 2-cell boundary
        offline = xarray.open_dataset(input_filename)
        online = offline[{'rlon': np.arange(2, offline.rlon.size - 2),
                          'rlat': np.arange(2, offline.rlat.size - 2)}]
        online.to_netcdf(output_filename)
        offline.close()

    elif args.task in ['gen-nml']:
        if cfg is None:
            raise RuntimeError("Please supply a config file.")

        output_path = os.path.join(cfg.output_path, "..")
        emiproc.misc.create_input_tracers(cfg, output_path)

    else:
        raise ValueError('Unknown task "%s"' % task)


if __name__ == '__main__':
    main()
