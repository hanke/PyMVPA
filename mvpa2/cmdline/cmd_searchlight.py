# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Apply a searchlight analysis to a data set that is already preprocessed and stored as Nifti file.
"""

# WiP: WORK IN PROGRESS and far from being functional

# WZ XXX: How to catch error messages and reduce them to a readibility that an non-pythonian user is not startled to much?
""""""

__docformat__ = 'restructuredtext'

import argparse
from mvpa2.base import verbose
if __debug__:
    from mvpa2.base import debug
#from mvpa2.cmdline.helpers \
        #import parser_add_common_args, parser_add_common_opt, args2datasets, strip_from_docstring, \
               #param2arg, ca2arg
from mvpa2.cmdline.helpers \
        import parser_add_common_args, parser_add_common_opt

# import routines specific for this analysis
from mvpa2.datasets.mri         import map2nifti
from mvpa2.generators.partition import NFoldPartitioner
from mvpa2.measures.base        import CrossValidation
from mvpa2.measures.searchlight import sphere_searchlight
from mvpa2.misc.errorfx         import mean_match_accuracy
from mvpa2.misc.io              import SampleAttributes

import os as os  # WZ: temporary

parser_args = {
    'description': '''Apply a searchlight analysis to a data set
that is already preprocessed and stored as Nifti file.''',
    'epilog': '''Example Usage:
        pymvpa2 searchlight pp4D_data attributes.txt
        pymvpa2 searchlight pp4D_data attributes.txt --clf SLMR --rad 5 --part 'n-2'
''',
    'formatter_class': argparse.RawDescriptionHelpFormatter
} # WZ TODO: use Haxby data for example usage - How make data path variable available in BASH?

# define command line arguments
def setup_parser(parser):
    # order of calls is relevant!
    # WZ XXX: How to ensure that all arguments are defined needed by required helper functions?

    parser_add_common_args(parser, pos=['multidata'])
    parser.add_argument('attr',  help='attribute file')

    inputargs = parser.add_argument_group('input data arguments')
    parser_add_common_opt(inputargs, 'multimask', names=('-m', '--mask'))

    inputargs.add_argument('--dtr',   action='store_true',
                           help='apply detrending on the data set.') # WZ TODO: specify polynomal order?
    inputargs.add_argument('--mc', '--mcpar',  default=None,
                           help='Motion correction parameter file from the mcflirt tool of the FSL package.')
    inputargs.add_argument('--no_z', dest='zscr',   action='store_false',
                           help='do not apply z-scoring to the data set')
    inputargs.add_argument('--avrg',  action='store_true',
                           help='use a chunk wise average of the targets for the analysis')
    inputargs.add_argument('-s', '--subset', default=None,
                           help='Create an additional volume containing the numbers of voxel within the searchlight sphere.')

    clfopt = parser.add_argument_group('classification options')
    parser_add_common_opt(clfopt, 'classifier',  names=('-c', '--clf'))
    parser_add_common_opt(clfopt, 'partitioner', names=('-p', '--part'))

    slopt = parser.add_argument_group('searchlight options')
    slopt.add_argument('-r', '--rad',    default=3, type=int,
                        help='sphere radius in voxel')
    slopt.add_argument('-v', '--nvxl',   action='store_true',
                        help='Create an additional volume containing the numbers of voxel within the searchlight sphere.')
    slopt.add_argument('-n', '--nproc',  dest='NumProc', default=1, type=int,
                        help='number of threads claimed for the analysis')

    outopts = parser.add_argument_group('output options')
    outopts.add_argument('-d', '--odir',   default=os.getcwd(),
                         help='output directory')
    parser_add_common_opt(outopts, 'output_prefix')
    outopts.add_argument('--plot',   action='store_true',
                         help='Create plots for sample distance and accuracy histograms')

# prepare data set for analysis
# WZ XXX: This is something for the helpers again (or is already there and I was to f...g s...d).
def prep_nifti_ds(args):
    from mvpa2.datasets.mri    import fmri_dataset
    from mvpa2.mappers         import zscore
    from mvpa2.mappers.detrend import poly_detrend

    attr = SampleAttributes(args.attr)
    ds = fmri_dataset(args.data, targets=attr.targets, chunks=attr.chunks, mask=args.mask) # WZ TODO: check if mask is specified
    verbose(1, "Data set loaded.")
    verbose(2, "loaded data set: %i" % args.ds)
    verbose(2, "attribute file:  %i" % args.attr)

    if not args.mcpar == None:
        from mvpa2.misc.fsl.base import McFlirtParams
        mc = McFlirtParams(path.join('mvpa2', 'data', 'bold_mc.par'))
        for param in mc:
            ds.sa['mc_' + param] = mc[param]
        res = poly_detrend(ds, opt_regs=['mc_x',    'mc_y',    'mc_z',
                                         'mc_rot1', 'mc_rot2', 'mc_rot3'])
        verbose(1, "Applied polynomial detrending includng motion correction parameter.")
        verbose(2, "MC parameter file:  %i" % args.mcpar)

    elif args.dtr:
        poly_detrend(ds, chunks_attr='chunks')
        verbose(1, "Applied polynomial detrending.")

    if args.zscr:
        zscore(ds, chunks_attr='chunks')  # apply z-scoring run-wise (TODO: add option to specify a baseline condition?)
        verbose(1, "Applied z scoring.")

    if args.avrg:
        from mvpa2.mappers.fx import mean_group_sample
        run_averager = mean_group_sample(['targets', 'chunks'])
        ds = ds.get_mapped(run_averager) # WZ TODO: import get_mapped
        verbose(1, "Calculated chunk wise average for the targets.")

    if args.sel == None:
        cds = ds
    else:
        import numpy.in1d
        cds = ds[in1d(ds.T, args.sel)]
        verbose(1, "Reduced data to a subset.")
        verbose(2, "Data subset includes targets:  %i" % args.sel)

    return ds

# execute core routines for the search light analysis
def run(args):
    if __debug__:
        debug('CMDLINE', "loading input data from %s" % args.data)

    ds = prep_nifti_ds(args)

    ### select the classifier
    clf = chose_clf(args.clf)

    # WZ: implement option for HalfPartitioner and OddEvenPartitioner
    splt = NFoldPartitioner(cvtype=args.cvtype, attr='chunks')

    cv = CrossValidation(clf, splt, errorfx=mean_match_accuracy) # WZ XXX: option for errorfx?
    sl = sphere_searchlight(cv, radius=args.rad, space='voxel_indices', nproc=args.nproc) # WZ XXX: check, if number of threads are available?

    sl_map = sl(ds)  # this starts the search light analysis with the previosly specified parameters

    niftiresults = map2nifti(sl_map, imghdr=ds.a.imghdr)
    niftiresults.to_filename(os.path.join(args.odir, args.onm+'.nii.gz')) # WZ XXX: routine to remove nii.gz extension to ensure proper file stem?

    if args.plot:
        print("implementd plotting here!")

    if args.nvxl:
        print("determine searlight sizes here!")
