import os
import subprocess
import sys

from yarnutils import *

srcdir = os.environ["SRCDIR"]
datadir = os.environ["DATADIR"]

vars = Variables(datadir)
