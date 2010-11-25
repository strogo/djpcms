#!/usr/bin/env python

if __name__ == '__main__':
    import djpcms
    import sys
    tags = sys.argv[1:]
    djpcms.runtests(tags = tags)