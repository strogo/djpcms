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
    return parser

if __name__ == '__main__':
    import djpcms
    import sys
    options, tags = makeoptions().parse_args()
    verbosity = options.verbosity
    
    p = os.path
    path = p.join(p.split(p.abspath(__file__))[0],'tests')
    sys.path.insert(0, path)
    from testrunner import run
    run(tags, verbosity = verbosity)