#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

def test(depth = 0):
    frame = sys._getframe(depth)
    code = frame.f_code

    print "frame depth = ", depth
    print "func name = ", code.co_name
    print "func filename = ", code.co_filename
    print "func lineno = ", code.co_firstlineno
    print "func locals = ", frame.f_locals

def main():
    test(0)
    print "--------"
    test(1)

if __name__ == "__main__":
    main()
