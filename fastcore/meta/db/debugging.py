# import
from debuggable.utils import *
import debuggable.utils as du
whatinside(du, dun=True)


# start
defaults.name = "delegates" # required
checksrc() # optional
# required
defaults.startsrc = "if to is None"
defaults.endsrc = "from_f.__annotations__.update(anno)"
displaysrc()


# dbcodes
dblst = defaults.srcdbps

srcline = """

"""
len(defaults.src.split(srcline)) # must be 2 to be right
dbcode = """

"""
dblst.append([(srcline, dbcode)])

# debugging 
delegates = dbsrclines([1,2], retn=True) # print out the debuggable source code under investgation
defaults.eg = """

"""
# actual code