# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
<<<<<<< HEAD
"""Apply a searchlight analysis to a data set that is already preprocessed and stored as Nifti file.
"""

# WiP: WORK IN PROGRESS and far from being functional

# WZ XXX: How to catch error messages and reduce them to a readibility that an non-pythonian user is not startled to much?
=======
""""""


# WORK IN PROGRESS
>>>>>>> c5f1a2dcd47c8bf9f4fe30558a148e996113febc

__docformat__ = 'restructuredtext'

import argparse
<<<<<<< HEAD
from mvpa2.base import verbose
=======
from mvpa2.base import verbose  # WZ: How is verbose mode enabled or switched off?
>>>>>>> c5f1a2dcd47c8bf9f4fe30558a148e996113febc
if __debug__:
    from mvpa2.base import debug
from mvpa2.cmdline.helpers \
        import parser_add_common_args, args2datasets, strip_from_docstring, \
               param2arg, ca2arg

# import routines specific for this analysis
<<<<<<< HEAD
from mvpa2.datasets.mri         import map2nifti
from mvpa2.generators.partition import NFoldPartitioner
=======
from mvpa2.datasets.mri         import fmri_dataset, map2nifti
from mvpa2.generators.partition import NFoldPartitioner
from mvpa2.mappers              import zscore
>>>>>>> c5f1a2dcd47c8bf9f4fe30558a148e996113febc
from mvpa2.measures.base        import CrossValidation
from mvpa2.measures.searchlight import sphere_searchlight
from mvpa2.misc.errorfx         import mean_match_accuracy
from mvpa2.misc.io              import SampleAttributes

<<<<<<< HEAD
import os as os

parser_args = {
    'description': 'Apply a searchlight analysis to a data set that is already preprocessed and stored as Nifti file.',
    'epilog': '''Example Usage:
                               pymvpa2 searchlight pp4D_data --attr attributes.txt
                               pymvpa2 searchlight pp4D_data --attr attributes.txt --clf SLMR --rad 5 --cvtype 2
''',
} # WZ TODO: use Haxby data for example usage - How make data path variable available in BASH?
=======
parser_args = {
    'description': 'Carry out serachlight analysis.',
    'epilog': '',
}
>>>>>>> c5f1a2dcd47c8bf9f4fe30558a148e996113febc

# define command line arguments
def setup_parser(parser):
    # order of calls is relevant!
<<<<<<< HEAD
    # WZ XXX: How to ensure that all arguments are defined needed by required helper functions?

    inputargs = parser.add_argument_group('input data arguments')
    parser_add_common_args(inputargs, pos=['multidata'], opt=['multimask'])
    inputargs.add_argument('ds',  help='data set')
    #inputargs.add_argument('-m', '--mask',  default=None, help='mask file')
    inputargs.add_argument('-a', '--attr',  required=True, help='attribute file')
    inputargs.add_argument('--nozscr',   action='store_false', help='do not apply z-scoring to the data set')
    inputargs.add_argument('-s', '--subset', default=None, help='Create an additional volume containing the numbers of voxel within the searchlight sphere.')
    inputargs.add_argument('--mc', '--mcpar',  default=None, help='Motion correction parameter file from the mcflirt tool of the FSL package.')
    inputargs.add_argument('--dtr',   action='store_true', help='apply detrending on the data set.') # WZ TODO: specify polynomal order?
    inputargs.add_argument('--avrg',  action='store_true', help='use a chunk wise average of the targets for the analysis')

    inputargs = parser.add_argument_group('classification options')
    inputargs.add_argument('-c', '--clf',    default="LinearCSVMC", help='applied classifier')
                                                    #currently implemented: "LinearCSVMC", "LinearNuSVMC", "SMLR", "GNB", "kNN", "BLR", "GPR",
                                                    #"glmnet", "GPR", "PLR", "RbfCSVMC", "RbfNuSVMC"')
    inputargs.add_argument('-t', '--cvtype', default=1, type=int, help='number of chunks used as test set')

    inputargs = parser.add_argument_group('searchlight options')
    inputargs.add_argument('-r', '--rad',    default=3, type=int, help='sphere radius in voxel')
    inputargs.add_argument('-v', '--nvxl',   action='store_true', help='Create an additional volume containing the numbers of voxel within the searchlight sphere.')
    inputargs.add_argument('-n', '--nproc',  dest='NumProc', default=1, type=int, help='number of threads claimed for the analysis')

    inputargs = parser.add_argument_group('output options')
    inputargs.add_argument('-d', '--odir',   default=os.getcwd(), help='output directory')
    inputargs.add_argument('-o', '--onm',    default="MVPA_SearchLight.nii.gz", help='output file name stem')
    inputargs.add_argument('-p', '--plot',   action='store_true', help='Create plots for sample distance and accuracy histograms')

=======
    inputargs = parser.add_argument_group('input data arguments')
    parser_add_common_args(inputargs, pos=['multidata'], opt=['multimask'])    
  
    #inputargs.add_argument('ds',  help='data set')
    #inputargs.add_argument('-mask',  default=None, help='mask file')
    inputargs.add_argument('-a, --attr',   required=True, help='attribute file') # include option to specify alternatively a subset of chunks and targets, that wil be repeated
    inputargs.add_argument('-n, --nproc',  dest='NumProc', default=1, type=int, help='number of threads claimed for the analysis')
    inputargs.add_argument('-r, --rad',    default=3, type=int, help='sphere radius in voxel')
    inputargs.add_argument('-t, --cvtype', default=1, type=int, help='number of chunks used as test set')
    inputargs.add_argument('-d, --odir',   default=os.getcwd(), help='output directory')
    inputargs.add_argument('-o, --onm',    default="MVPA_SearchLight.nii.gz", help='output file name stem')
    inputargs.add_argument('-c, --clf',    default="LinearCSVMC", help='applied classifier -
                                                    currently implemented: "LinearCSVMC", "LinearNuSVMC", "SMLR", "GNB", "kNN", "BLR", "GPR",
                                                    "glmnet", "GPR", "PLR", "RbfCSVMC", "RbfNuSVMC"')
    inputargs.add_argument('-p, --plot',   action='store_true', help='Create plots for sample distance and accuracy histograms')
    inputargs.add_argument('-v, --nvxl',   action='store_true', help='Create an additional volume containing the numbers of voxel within the searchlight sphere.')
    inputargs.add_argument('-s, --subset', default='none', help='Create an additional volume containing the numbers of voxel within the searchlight sphere.')
       
>>>>>>> c5f1a2dcd47c8bf9f4fe30558a148e996113febc
def chose_clf(clfstr):  # WZ: put this together with the input arguments to the helpers? Add classifier specific arguments?
    if "LinearCSVMC" in clfstr:
        import mvpa2.clfs.svm.LinearCSVMC
        clf = LinearCSVMC()
    if "LinearNuSVMC" in clfstr:
        import mvpa2.clfs.svm.LinearNuSVMC
        clf = LinearNuSVMC()
    if "SMLR" in clfstr:
        import mvpa2.clfs.smlr.SMLR
        clf = SMLR()
    if "GNB" in clfstr:
        import mvpa2.clfs.gnb.GNB
        clf = GNB()
    if "kNN" in clfstr:
        import mvpa2.clfs.knn.kNN
        clf = kNN()
    elif "BLR" in clfstr:
        import mvpa2.clfs.blr.BLR
        clf = BLR()
    elif "glmnet" in clfstr:
        import mvpa2.clfs.glmnet.GLMNET_C
        clf = GLMNET_C()
    elif "GPR" in clfstr:
        import mvpa2.clfs.gpr.GPR
        clf = GPR()
    elif "PLR" in clfstr:
        import mvpa2.clfs.plr.PLR
        clf = PLR()
    elif "RbfCSVMC" in clfstr:
        import mvpa2.clfs.svm.RbfCSVMC
        clf = RbfCSVMC()
    elif "RbfNuSVMC" in clfstr:
        import mvpa2.clfs.svm.RbfNuSVMC
        clf = RbfNuSVMC()
<<<<<<< HEAD
    else:
        print("ERROR: unknown classifier!")
    return clf

# prepare data set for analysis
# WZ XXX: This is something for the helpers again (or is already there and I was to f...g s...d).
def prep_nifti_ds(args):
    from mvpa2.datasets.mri    import fmri_dataset
    from mvpa2.mappers         import zscore
    from mvpa2.mappers.detrend import poly_detrend

    attr = SampleAttributes(args.attr)
    ds = fmri_dataset(args.ds, targets=attr.targets, chunks=attr.chunks, mask=args.mask)
    verbose(1, "Data set loaded.")
    verbose(2, "loaded data set: %i" % args.ds)
    verbose(2, "attribute file:  %i" % args.attr)

    if not args.mcpar == None:
        from mvpa2.misc.fsl.base import McFlirtParams
        mc = McFlirtParams(path.join('mvpa2', 'data', 'bold_mc.par'))
        # merge the correction parameters into the dataset itself
        for param in mc:
            ds.sa['mc_' + param] = mc[param]
        res = poly_detrend(ds, opt_regs=['mc_x',    'mc_y',    'mc_z',
                                        'mc_rot1', 'mc_rot2', 'mc_rot3'])
        verbose(1, "Applied polynomial detrending includng motion correction parameter.")
        verbose(2, "MC parameter file:  %i" % args.mcpar)

    elif args.dtr:
        poly_detrend(ds, chunks_attr='chunks')
        verbose(1, "Applied polynomial detrending.")

    if args.nozscr:
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

=======
    else
        print("ERROR: unknown classifier!")
    return clf

# select subsets based on the targets
def ds_subset(ds, sel):
    if "none" in sel:
        cds = ds
    else
        import numpy.in1d
        cds = ds[in1d(ds.T,sel)]
    return cds
            
>>>>>>> c5f1a2dcd47c8bf9f4fe30558a148e996113febc
# execute core routines for the search light analysis
def run(args):
    if __debug__:
        debug('CMDLINE', "loading input data from %s" % args.data)
<<<<<<< HEAD

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

=======
    dss = args2datasets(args.data, args.masks)
    verbose(1, "Loaded %i input datasets" % len(dss))

    attr = SampleAttributes(params.attr)
    ds = fmri_dataset(params.ds, targets=attr.targets, chunks=attr.chunks, mask=params.mask)
    zscore(ds, chunks_attr='chunks')  # apply zsoring run-wise

    ds = ds_subset(ds, params.sel) # select subset of data

    ### select the classifier
    clf = chose_clf(params.clf)

    # WZ: implement option for HalfPartitioner and OddEvenPartitioner
    splt = NFoldPartitioner(cvtype=params.cvtype, attr='chunks')  

    cv = CrossValidation(clf, splt, errorfx=mean_match_accuracy) # WZ: option for errorfx?
    sl = sphere_searchlight(cv, radius=params.rad, space='voxel_indices', nproc=params.nproc) # WZ: check, if number of threads are available?

    sl_map = sl(ds)  # this starts the search light analysis with the previosly specified parameters
   
    niftiresults = map2nifti(sl_map, imghdr=ds.a.imghdr)
    niftiresults.to_filename(os.path.join(params.odir, params.onm+'.nii.gz')) # WZ: routine to remove nii.gz extension to ensure proper file stem?

    if params.plot:
        print("implementd plotting here!")

    if params.nvxl:
        print("determine searlight sizes here!")
        
>>>>>>> c5f1a2dcd47c8bf9f4fe30558a148e996113febc
