# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
""""""


# WORK IN PROGRESS

__docformat__ = 'restructuredtext'

import argparse
from mvpa2.base import verbose  # WZ: How is verbose mode enabled or switched off?
if __debug__:
    from mvpa2.base import debug
from mvpa2.cmdline.helpers \
        import parser_add_common_args, args2datasets, strip_from_docstring, \
               param2arg, ca2arg

# import routines specific for this analysis
from mvpa2.datasets.mri         import fmri_dataset, map2nifti
from mvpa2.generators.partition import NFoldPartitioner
from mvpa2.mappers              import zscore
from mvpa2.measures.base        import CrossValidation
from mvpa2.measures.searchlight import sphere_searchlight
from mvpa2.misc.errorfx         import mean_match_accuracy
from mvpa2.misc.io              import SampleAttributes

parser_args = {
    'description': 'Carry out serachlight analysis.',
    'epilog': '',
}

# define command line arguments
def setup_parser(parser):
    # order of calls is relevant!
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
            
# execute core routines for the search light analysis
def run(args):
    if __debug__:
        debug('CMDLINE', "loading input data from %s" % args.data)
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
        
