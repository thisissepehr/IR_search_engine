import sys
from os import system

system("python3 ../../py/search.py"+" -q '"+sys.argv[1]+"' -m "+sys.argv[2])
