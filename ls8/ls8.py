#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *
from cpu_copy import *

cpu = CPU()
# cpuCOPY = CPUCOPY()

cpu.load()
cpu.run()
# cpuCOPY.load("examples/print8.ls8")
# cpuCOPY.run()
