#!/usr/bin/env python
import os
import sys
from optparse import OptionParser

def makeoptions():
    parser = OptionParser()
    parser.add_option("-v", "--verbosity",
                      type = int,
                      action="store",
                      dest="verbosity",
                      default=1,
                      help="Tests verbosity level, one of 0, 1, 2 or 3")
    parser.add_option("-l", "--list",
                      action="store_true",
                      dest="show_list",
                      default=False,
                      help="Show the list of available test labels for a given test type")
    parser.add_option("-f", "--fail",
                      action="store_false",
                      dest="can_fail",
                      default=True,
                      help="If set, the tests won't run if there is an import error in tests")
    parser.add_option("-t", "--type",
                      action="store",
                      dest="test_type",
                      default='regression',
                      help="Test type, possible choices are:\n\
                      * regression (default)\n\
                      * bench\n\
                      * profile")
    return parser


def addpath():
    # add the tests directory to the Python Path
    p = os.path
    path = p.split(p.abspath(__file__))[0]
    if path not in sys.path:
        sys.path.insert(0, path)
    path = p.join(path,'tests')
    if path not in sys.path:
        sys.path.insert(0, path)
    
addpath()


if __name__ == '__main__':
    options, tags = makeoptions().parse_args()
    from testsrunner import run
    run(tags,
        test_type = options.test_type,
        can_fail=options.can_fail,
        verbosity=options.verbosity,
        show_list=options.show_list)