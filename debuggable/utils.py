# AUTOGENERATED! DO NOT EDIT! File to edit: ../utils.ipynb.

# %% auto 0
__all__ = ['defaults', 'whatinside', 'whichversion', 'checksource', 'alignright', 'dbcolors', 'colorize', 'dbprint',
           'insert2debug', 'dbsrclines', 'displaysavedbsrc', 'checksrc', 'strip_ansi', 'matchsrcorder', 'displaysrc']

# %% ../utils.ipynb 3
from inspect import getmembers, isfunction, isclass, isbuiltin, getsource
import os.path, pkgutil
from pprint import pprint
import re
import ast
import inspect
from fastcore.meta import *
from fastcore.imports import *

# %% ../utils.ipynb 5
def whatinside(mo, # module, e.g., `import fastcore.all as fa`, use `fa` here
               dun:bool=False, # print all items in __all__
               func:bool=False, # print all user defined functions
               clas:bool=False, # print all class objects
               bltin:bool=False, # print all builtin funcs or methods
               lib:bool=False, # print all the modules of the library it belongs to
               cal:bool=False # print all callables
             ): 
    'Check what inside a module: __all__, functions, classes, builtins, and callables'
    dun_all = len(mo.__all__) if hasattr(mo, "__all__") else 0
    funcs = getmembers(mo, isfunction)
    classes = getmembers(mo, isclass)
    builtins = getmembers(mo, isbuiltin)
    callables = getmembers(mo, callable)
    pkgpath = os.path.dirname(mo.__file__)
    print(f"{mo.__name__} has: \n{dun_all} items in its __all__, and \n{len(funcs)} user defined functions, \n{len(classes)} classes or class objects, \n{len(builtins)} builtin funcs and methods, and\n{len(callables)} callables.\n")  
    if hasattr(mo, "__all__") and dun: pprint(mo.__all__)
    if func: 
        print(f'The user defined functions are:')
        pprint([i[0] for i in funcs])
    if clas: 
        print(f'The class objects are:')
        pprint([i[0] for i in classes])
    if bltin: 
        print(f'The builtin functions or methods are:')
        pprint([i[0] for i in builtins])
    if cal: 
        print(f'The callables are: ')
        pprint([i[0] for i in callables])
    if lib: 
        modules = [name for _, name, _ in pkgutil.iter_modules([pkgpath])]
        print(f'The library has {len(modules)} modules')
        pprint(modules)

# %% ../utils.ipynb 12
from importlib.metadata import version, metadata, distribution
from platform import python_version 

# %% ../utils.ipynb 13
def whichversion(libname:str, # library name
                req:bool=False, # print lib requirements 
                file:bool=False): # print all lib files
    "Give you library version and other basic info."
    if libname=='python':
        print(f"python: {python_version()}")
    else: 
        print(f"{metadata(libname)['Name']}: {version(libname)} \n{metadata(libname)['Summary']}\
    \n{metadata(libname)['Author']} \n{metadata(libname)['Home-page']} \
    \npython_version: {metadata(libname)['Requires-Python']} \
    \n{distribution(libname).locate_file(libname)}")

    if req: 
        print(f"\n{libname} requires: ")
        pprint(distribution(libname).requires)
    if file: 
        print(f"\n{libname} has: ")
        pprint(distribution(libname).files)
    

# %% ../utils.ipynb 96
def checksource():
    lst = defaults.src.split('\n')
    for l in lst: 

        if l.strip() in defaults.deb:
            print('{:<157}'.format(l))
        else: 
            print('{:=<157}'.format(l))
    defaults.deb = None # make sure defaults.deb set to None for later debugging srcode.

# %% ../utils.ipynb 97
defaults = type('defaults', (object,), {'block': False, # whether inside a block of code investigation or not
                                     'src': None, # store the source code of the functiong being debugged
                                     'deb': None, # store the debuggable source code
                                     'debp': None, # store the debuggable source code for color printing
                                     'name': None, # the name of the func to be debugged
                                     'startsrc': None, # a piece of str in the starting line of the src code
                                     'endsrc': None, # a piece of str in the ending line of the src code
                                     'eg': None, # save an example in str
                                     'margin': 157, # for align to the right
                                     'multi': False, # debugging multiline source codes
                                     'src2dbp': type('fastcore.meta', (object,), {'delegates': [], # a list of lists of (srcline, dbcode) 
                                                                                  'delegatesdb': None, # the debuggable source
                                                                                 }) # store a list of (srcline, dbcode)
                                    }) 

# %% ../utils.ipynb 142
def alignright(blocks):
    lst = blocks.split('\n')
    maxlen = max(map(lambda l : len(l) , lst ))
    indent = defaults.margin - maxlen
    for l in lst:
        print(' '*indent + format(l))

# %% ../utils.ipynb 147
class dbcolors:
    g = '\033[92m' #GREEN
    y = '\033[93m' #YELLOW
    r = '\033[91m' #RED
    reset = '\033[0m' #RESET COLOR

# %% ../utils.ipynb 148
def colorize(cmt, color:str=None):
    if color == "g":
        return dbcolors.g + cmt + dbcolors.reset
    elif color == "y":
        return dbcolors.y + cmt + dbcolors.reset
    elif color == "r":
        return dbcolors.r + cmt + dbcolors.reset
    else: 
        return cmt

# %% ../utils.ipynb 154
def dbprint(src:str, # the source to debug in str
            cmt:str,
            *code,   # a number of codes to run, each code is in str, e.g., "a + b", "c = a - b"
            **env
           ):  # a number of stuff needed to run the code, e.g. var1 = var1, func1 = func1
    "Insert and run your codes and give readable output during debugging. Caution 1: \
    avoid using the same variable name used in both global and local scopes, e.g., \
    use `k` in the func and use `k` again inside a for loop inside the func.\
    Caution 2: make sure to include all the necessary env variables to avoid \
    the same variable with different values from different scopes. Caution 3: when an env variable is updated, \
    then you need to includ it again in the next dbprint. Caution 4: be strict on the spaces, e.g., `for k,v in` \
    and `a = createsth(...)`"
    
    # Inside the source code, ff you ever add a block of multiline codes like `for in` or `if`, and run dbprint for each line of the block, then set 
    # defaults.block to True
    if defaults.block == True:
        print('\n')
        print('{:>157}'.format("===source inside a block==="))
        print('{:>157}'.format(src))
        print('\n')
        # print(src + "<===== source code =======") 

    else:
        print('\n')
        # print('{:>157}'.format("======================== source code ==========================="))
        print('{:#^157}'.format(" source code with lines under investigation "))
        print('\n')
        # print('{:<157}'.format(src))        
        
        # print the source code of the function
        lst = defaults.src.split('\n')

        ccount = 0
        for l in lst: 
            if bool(l) and l.strip() in src: # how to make sure all these ls are close to each other???
                print('{:=<157}'.format(l))
                ccount = ccount + 1
                
                if bool(cmt): # make sure the comments are colored and aligned to the most right
                    # if this is the last srcline of the srcblock under investigation
                    numsrclines = len(src.split("\n"))
                    if ccount == numsrclines:
                        colcmt = colorize(cmt, "r")
                        alignright(colcmt)
                    # clst = cmt.split('\n') 
                    # if ccount <= len(clst)-1:
                    #     # print('{:>157}'.format(colorize(clst[ccount], "r")))
                    #     colcmt = colorize(clst[ccount], "r")
                    #     alignright(colcmt)
                    #     ccount = ccount + 1

            else: 
                print('{:<157}'.format(l))

        # print out the example
        print('{:<157}'.format(defaults.eg))
        
    
    # trial and error version for real code, still not quite why globals vs locals work in exec and eval
    for c in code:
        print("\n")
        
        # handle a block of code
        if "\n" in c: 
            output = f"Running your code block => "
            print('{:<157}'.format(c))       
            print('{:>157}'.format(output))  
            print('The code block printout => : ')
            block = ast.parse(c, mode='exec')
            exec(compile(block, '<string>', mode='exec'), globals().update(env))
        
        # handle assignment: 2. when = occur before if; 1. when no if only =
        elif ("=" in c and "if" not in c) or ("=" in c and c.find("=") < c.find("if")): # make sure assignment and !== and == are differentiated
            
            # print('k' in locals())
            exec(c, globals().update(env)) 
            # print('k' in locals())
            variable = c.partition(" = ")[0]
            # print(f"{c} => {variable}: {eval(variable)}")
            output = f"{c} => {variable}: {eval(variable)}"
            print('{:>157}'.format(output))       
            
        # handle if statement
        # Note: do insert code like this : `if abc == def: print(abc)`, print is a must
        elif "if" in c: 
            cond = re.search('if (.*?):', c).group(1)
            
            # when code in string is like 'if abc == def:'
            if c.endswith(':'):
                
                # print ... 
                # print(f"{c} => {cond}: {eval(cond)}")      
                output = f"{c} => {cond}: {eval(cond)}"
                print('{:>157}'.format(output))
                
            # when code in string is like 'if abc == def: print(...)'
            else: 
                # if the cond is true, then print ...
                if eval(cond):
                    
                    # "if abc == def: print(abc)".split(': ', 2)[1] to get 'print(abc)'
                    printc = c.split(': ', 1)[1]
                    # print(f"{c} => {printc} : ")
                    output = f"{c} => {printc} : "
                    print('{:>157}'.format(output))      
                    exec(c, globals().update(env))
                    
                # if cond is false, then print ...
                else: 
                    # print(f"{c} => {cond}: {eval(cond)}")
                    output = f"{c} => {cond}: {eval(cond)}"
                    print('{:>157}'.format(output))   
                
                
        # handle for in statement
        elif "for " in c and " in " in c:           
            
            # in example like 'for k, v in abc:' or `for k, v in abc: print(...)`, if abc is empty
            # step 1: access abc
            # get the substring between 'in ' and ':', which is like 'abc'
            abc = re.search('in (.*?):', c).group(1)
            # if abc is empty dict or list: print and pass
            if not bool(eval(abc)): 
                # print(f'{c} => {abc} is an emtpy {type(eval(abc))}')
                output = f'{c} => {abc} is an emtpy {type(eval(abc))}'
                print('{:>157}'.format(output))   
                continue 
                # The break statement can be used if you need to break out of a for or while loop and move onto the next section of code.
                # The continue statement can be used if you need to skip the current iteration of a for or while loop and move onto the next iteration.
            
            # if the code in string is like 'for k, v in abc:', there is no more code after `:`
            if c.endswith(':'):
                
                # get the substring between 'for ' and ' in', which is like 'k, v'
                variables = re.search('for (.*?) in', c).group(1)
                
                # if variables has a substring like ', ' inside
                if (',') in variables: 
                    
                    # split it by ', ' into a list of substrings
                    vl = variables.split(',')
                    key = vl[0]
                    value = vl[1]
                    
                    # make sure key and value will get evaluated first before exec run
                    # printc is for exec to run
                    printc = "print(f'{key}:{eval(key)}, {type(eval(key))} ; {value}:{eval(value)}, {type(eval(value))}')" 
                    # printmsg is for reader to understand with ease
                    printmsg = "print(f'key: {key}, {type(key)} ; value: {value}, {type(value)}')"
                    c1 = c + " " + printc
                    # print(f"{c} => {printmsg} : ")      
                    output = f"{c} => {printmsg} : "
                    print('{:>157}'.format(output))   
                    exec(c1, globals().update(env))
                
                else:
                    printc = "print(f'{variables} : {eval(variables)}')"
                    printmsg = "print(f'i : {variables}')"
                    c1 = c + " " + printc
                    # print(f"{c} => {printmsg} : ")     
                    output = f"{c} => {printmsg} : "
                    print('{:>157}'.format(output))   
                    exec(c1, globals().update(env))
                    
            # if the code in string is like 'for k, v in abc: print(abc)'
            else:                 
                # "for k, v in abc: print(k)".split(': ', 1)[1] to get 'print(k)'
                printc = c.split(': ', 1)[1]
                # print(f"{c} => {printc} : ")
                output = f"{c} => {printc} : "
                print('{:>157}'.format(output))   
                exec(c, globals().update(env)) # we can't use eval to run `for in` loop, but exec can.
            ### Note: we shall not use the expression like `for k, v in abc print(abc)`
            ### Note: we shall not use the expression like `for k, v in abc if k == def`
        
        
        # handle evaluation
        else: 
            # print(f"{c} => {c} : {eval(c, globals().update(env))}") 
            output = f"{c} => {c} : {eval(c, globals().update(env))}"
            print('{:>157}'.format(output))   
            
        # the benefit of using global().update(env) is 
        # to ensure we don't need to include the same env for the second time

# %% ../utils.ipynb 168
def insert2debug(name:str, # name of a function to debug, e.g., delegates
                 srcline:str, # e.g., "        if hasattr(from_f,'__delwrap__'): return f"
                 dbcode:str,  # str, e.g., "dbprint(...)"
                 run:bool=True, # run exec or not
                 dberror:bool=False, # choose to debug error in source code by setting return None or not
                 **env):
    "select a line or a block of source code and insert a dbprint above it and only output this dbprint result."
    
    # defaults.multi default to False, unless set True, defaults.deb is default to None before debugging srcode
    if defaults.multi and bool(defaults.deb): 
        srcode = defaults.deb
        srcodep = defaults.debp
        lstxtp = srcodep.split(srcline.strip()) # make sure the split is done properly
    else: 
        # srcode = inspect.getsource(eval(name, globals().update(env)))
        srcode = defaults.src
        
    lstxt = srcode.split(srcline)
    
    
    retn = "" 
    if dberror: 
        retn = retn + "\n        return None\n" #  to exit the function, "" to continue on

    
    insert = colorize(dbcode, "g") + colorize(retn, "y") + colorize(srcline, "r") 
    if bool(defaults.deb):
        src2print = lstxtp[0] + insert + lstxtp[1]
    else:
        src2print = lstxt[0] + insert + lstxt[1]
            
    src2db = lstxt[0] + dbcode + retn + srcline + lstxt[1] # make sure return is before srcline and after dbcode
    # save the entire source code with dbprints
    defaults.deb = src2db
    # save the entire source code with dbprints for color printing
    defaults.debp = src2print
    
    # to exec 
    if run: 
        exec(src2db, globals().update({'srcline': srcline})) # now a debuggable version of delegates is available to use
        # globals().update({name:eval(name)})
        return eval(name) # give this debuggable version of delegates to the notebook context
    # to not exec but only get the full debuggable source 
    else: 
        return None

# %% ../utils.ipynb 171
from fastcore.foundation import L

# %% ../utils.ipynb 181
def dbsrclines(lines:list = None, # if None then print all e.g., defaults.src2dbp.delegates
               dbsrc:bool = False, # get the full debuggable source code
               retn:bool = False # choose to add return None after the last dbcode
              ): 
    "Doing one line or multilines of insert2debug on source code with dbprints."
    srcname = defaults.name
    srcdblist = eval("defaults.src2dbp." + srcname)
    srcdblist = L(srcdblist)
    
    if len(lines) > 1: 
        defaults.multi = True
        lst = eval("srcdblist" + str(lines))
        for idx, i in zip(range(len(lst)), lst): # add retn to the last dbcode
            if retn and idx == len(lst)-1:
                delegates = insert2debug(srcname, i[0][0], i[0][1], dberror=True) ### add dberror to insert2debug
            else:
                delegates = insert2debug(srcname, i[0][0], i[0][1])

    else: 
        item = eval("srcdblist" + str(lines))
        if retn:
            delegates = insert2debug(srcname, item[0][0], item[0][1], dberror=True)  ### add dberror to insert2debug           
        else:
            delegates = insert2debug(srcname, item[0][0], item[0][1])

    # print out the colored dbsrc selected
    for l in defaults.debp.split("\n"):
        print(l)

    defaults.multi = False
    defaults.deb = None
    return delegates

# %% ../utils.ipynb 185
def displaysavedbsrc():
    "Doing one line or multilines of insert2debug on source code with dbprints."
    srcname = defaults.name
    srcdblist = eval("defaults.src2dbp." + srcname)
    srcdblist = L(srcdblist)
     
    
    defaults.multi = True
    for i in srcdblist:
        insert2debug(srcname, i[0][0], i[0][1], run=False) # don't exec, just add up debuggable source
        
    # export the debuggable source
    # defaults.src2dbp.delegatesdb = defaults.deb
    exec(f'defaults.src2dbp.{srcname}db = defaults.deb')
    # pprint(defaults.src2dbp.delegatesdb, width=157)
    dbsrclines = ""
    for l in srcdblist:
        dbsrclines = dbsrclines + l[0][0]
    for l in defaults.deb.split('\n'):
        if l.strip() in dbsrclines:
            print(colorize(l, 'g'))
        else:
            print(l)
    defaults.deb = None
    defaults.multi = False
    return None

# %% ../utils.ipynb 191
def checksrc():
    "check src code against dbsource. Also the latest srcode is stored inside defaults.src."
    srcname = defaults.name
    defaults.src = inspect.getsource(eval(srcname))

    # now dbsrc == defaults.src2dbp.delegatesdb
    dbsrc = eval("defaults.src2dbp." + srcname + "db")
    count = 0

    lst = defaults.src.split('\n')
    for l in lst: 
        if not bool(dbsrc):
            print(l)
        elif bool(dbsrc) and l.strip() in dbsrc:
            tick = f'(\u2713)'
            indent = defaults.margin - len(l) - len(tick)
            print(l + " "*indent + tick)    
        else: 
            print('{:=<157}'.format(l))
            count = count + 1
            
    if bool(dbsrc) == False: 
        print(f'your debuggable srcode is empty. You have not written any, or you have lost your defaults.src2dbp.{srcname}db or db/{srcname}db file.')
    if count > 0: 
        raise Exception(f'{srcname} has updated on {count} lines, you need to update your debuggable codes too.')

# %% ../utils.ipynb 192
def strip_ansi(source):
    return re.sub(r'\033\[(\d|;)+?m', '', source)

# %% ../utils.ipynb 193
def alignright(blocks):
    lst = blocks.split('\n')
    maxlen = max(map(lambda l : len(strip_ansi(l)) , lst ))
    indent = defaults.margin - maxlen
    for l in lst:
        print(' '*indent + format(l))

# %% ../utils.ipynb 208
def matchsrcorder(srcdbps:list # the list contain all srclines and their dbcodes with random order
                 ):
    srcdbps1 = [] # a list to store the correct order of srclines and dbcodes
    for l in defaults.src.split("\n"):
        for idx, s in zip(range(len(srcdbps)), srcdbps):
            if l.strip() in s[0][0]:
                srcdbps.pop(idx)
                srcdbps1.append(s)  
    return srcdbps1

# %% ../utils.ipynb 216
def displaysrc():
    "display the official source code also marking the debuggable srclines"
    srcname = defaults.name # name of src code like delegates
    startsrc = defaults.startsrc # a piece of code like "if to is None"
    endsrc = defaults.endsrc # a piece of code like "from_f.__annotations__.update(anno)"
    
    srcdblist = eval("defaults.src2dbp." + srcname)
    srcdblist = L(srcdblist)
    
    idx = 0
    mark = False
    passl = False
    for l in defaults.src.split("\n"):

        # to mark the index for the targed src codes
        if startsrc in l: mark = True
        if mark:
            marker = f'( {idx} )' + "     "
            for idxi, i in zip(range(len(srcdblist)), srcdblist):

                if l.strip() in i[0][0]:

                    marker = f'( {idx} )' + f'=={idxi}=='
                    indent = defaults.margin - len(l) - len(marker)
                    print(l + "="*indent + marker)
                    passl = True
                    continue # jump out of the inner for loop

            if passl: # make sure to jump out of the outer for loop
                passl = False
                idx = idx + 1 # keep track idx for every srcline to be debugged
                continue
            indent = defaults.margin - len(l) - len(marker)
            print(l + " "*indent + marker)
            idx = idx + 1
            if endsrc in l: mark = False
        else:
            print(l)
