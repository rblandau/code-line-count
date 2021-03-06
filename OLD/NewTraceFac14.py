#!/usr/bin/python
# NewTraceFac.py
# 
# 
"""
NewTraceFac14 trace module
                                RBLandau 20080226
                                updated  20080830
                                updated  20081003
                                updated  20090207
                                updated  20090527
                                updated  20140114
                                updated  20140209
                                updated  20140315
                                updated  20140723
                                updated  20141020
                                updated  20150112
                                updated  20160921
                                updated  20170127
                                updated  20170129
                                
  Copyright (C) 2008,2009,2014,2015,2016,2017 Richard Landau.  All rights reserved.
  
  Redistribution and use in source and binary forms, with or
  without modification, are permitted provided that the following
  conditions are met:
  
      * Redistributions of source code must retain the above
  copyright notice, this list of conditions and the following
  disclaimer.
  
      * Redistributions in binary form must reproduce the above
  copyright notice, this list of conditions and the following
  disclaimer in the documentation and/or other materials provided
  with the distribution.
  
      * Neither the name of Richard Landau nor the names of other
  contributors may be used to endorse or promote products derived
  from this software without specific prior written permission.
  
  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
  CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from time       import localtime, sleep
from os         import getenv
from re         import findall
from functools  import wraps
'''
    RBLandau 20080824
    NewTraceFac tracelog facility for Python.
    Copyright (C) 2008, Richard Landau.  All rights reserved.
    Evolved from old PDP-11 assembler, C, C++, VB, Perl, and other 
     similar trace facilities that I have done over the years.  
     Originated in approximately 1978 and has been one-plussed 
     surprisingly only slightly over several decades.  

    Usage: 
    Set environment variables, if necessary, to specify the desired 
     level of detail, target (stdout or file), and filename, if necessary.  
     Note that no source code change is needed to turn tracing on and off, 
     or to redirect it to a file, only changes to the running environment.  
      export TRACE_LEVEL=3
      export TRACE_TARGET=4
      export TRACE_FILE="c:\trace file goes here for ease of finding.log"
     (Use export for *NIX and Cygwin systems; use SET for vanilla Windows.)
    Instantiate the NewTrace object and store it global static so that any 
     module can use it.  E.g., 
          gt As NewTrace = New NewTrace    (VB)
          NTRC = NewTraceFac()             (Python)
    Call the ntrace() method of that instance, giving detail level number
     and string.  E.g., 
          gt.trace(1,"This is an item at level 1")
          NTRC.ntrace(2,"This is an item at level 2")
          NTRC.ntracef(3,"FOO","The FOO facility says hi at level 3")
    If the TRACE_LEVEL specified in the program's environment is 
     greater than or equal to the detail level specified in the call, 
     then the string will be printed to the trace log.  
    If the ntracef() method is used, then additionally, the facility string
     specified in the call must match one of the facilities requested
     in the TRACE_FACIL environment variable.  If TRACE_FACIL is "ALL" or 
     the empty string ("") or null (not defined) or indecipherable, then 
     all facilities match, and all will be traced.  This is the default.
    The ntrace() method alone prints a blank facility code.

    The facility list may explicitly include and exclude 
     some facilities.  
    Examples:
      ""                   traces all named facilities
      "ALL"                traces all named facilities
      "NONE"               traces no named facilities
      "ALL -A" "all-a"     traces all named facilities except facility A
      "NONE A" "none+a"    traces only facility A
      "INDECIPHERABLECRUD" traces all named facilities.
    Trace calls using ntrace() with no facility name are always included.  
    Personally, I tend to restrict facility codes to exactly the same 
    length (in my case, four characters), again so that successive lines
    will have various fields aligned for easier recognition and searching.  
    Note that if you want only, say, facility A, then you must use
      export TRACE_FACIL=NONE+A
    to prevent other facilities from being listed.  

    A trace output line looks like 
          YYYYMMDD_HHMMSS L  user-specified string
     or 
          YYYYMMDD_HHMMSS L FACIL user-specified string
    HTML output is slightly different, includes a "<BR>" at the start 
     of each line.  
      HH is the 24-hour hour.
      L is the level of detail specified for this trace line.

    Environment variables used by trace() are
      TRACE_LEVEL, TRACE_TARGET, TRACE_FILE, and TRACE_PRODUCTION.  
      TRACE_LEVEL is mandatory, the others optional.  Explanations below.  

    Typical use of trace levels is:
    0     Messages that always should be printed, e.g., errors that 
          the user must see.
    1     Entries to functions, with arguments listed.
          Any internal error conditions or error exits from 
          functions, with status.  
    2     Normal exits from functions, with status and maybe output arg values.  
    3     Things that happen once per record, once per line, etc., 
          that are repeated often, big-O the number of lines in the file
          or messages in the stream.  
    4     Really detailed info, such as syntax cracking of input lines, 
          entries in data structures, and such, that happen once or more
          per line.  
    5     Really, really detailed info, such as routine accesses to 
          data structures.

    Contents of environment veriables:
    TRACE_LEVEL;    # integer: levels 0 (or absent) thru 5.  
                    If null, defaults to zero.  
    TRACE_TARGET;   # bitmask: target bits 1=print to stdout, 
                    2=print html to stdout, 4=print to file.
                    If null, defaults to 1 (print on stdout).  
    TRACE_FILE;     # file: name of log file to trace into.
                    If null, defaults to "./newtrace.log".
    TRACE_FACIL;    # list of facility names to be traced.
                    Normally a blank-separated list of 
                     facility names that will be included in
                     results of the tracef() call.
                    If "ALL", then all facilities will be
                     included.  If "NONE" then no facilities
                     will be included.  
                    Facilities can be explicitly included after
                     NONE, e.g., "NONE FOO" or "NONE +FOO".
                    Facilities can be explicitly excluded after 
                     ALL, e.g., "ALL -FOO".
                    If null, then ALL is assumed.
    TRACE_PRODUCTION;
                    If "YES" then nothing will be traced, and the 
                     trace functions and decorators will attempt 
                     to use as little CPU resource as possible.

Python decorators:
There are two new functions to use as Python decorators to
 report entry and exit of functions, including arguments in
 and return value out, painlessly.  
Input arguments cannot be identified by the decorator version
 of ntrace() and ntracef().  If you need individual identification 
 of input arguments, call the trace manually, as in the old days.  
    @ntrace             for calls with no facility code attached
    @ntracef("ABCD")    for calls associated with a facility ABCD
As usual, the facility code should be max four letters to preserve 
 alignment and should be all caps for legibility.  

The @ntrace decorator prints entry at level 1 and exit at level 2.

The @ntracef() decorator also supports an optional level argument to change
 the trace level of the entry and exit lines.  This can be specified 
 positionally or keyword, e.g., @ntracef("FOO",2) or @ntracef("FOO",level=2).
The @ntrace decorator does not support the level argument; but note that
 the facility on @ntracef() can be left blank, e.g., @ntracef("",5).  
The @ntracef decorator processes the first argument specially if 
 the argument is an instance pointer (usually "self" in class 
 methods).  In this case, it prints the classname, and the 
 instance's self.ID if it exists, on both entry and exit.  
 Much more informative than the hex address.  

Summary examples in Python:
from NewTraceFac import NTRC, ntrace, ntracef
NTRC.ntrace(3, "some string with %s %s" % ("some", "substitutions"))
NTRC.ntracef(3, "ABCD", "some string with %s %s" % ("some", "substitutions"))

New 2017: The decorators can be nulled out with the environment variable
    TRACE_PRODUCTION=YES
 This will also cause direct calls to the ntrace() and ntracef() functions
 to return with as little work as possible.  
'''

class CNewTrace:
    def __init__(self):
        self.setDefaults()

    def setDefaults(self,mylevel=0,mytarget=1,myfile="newtrace.log",
        myfacil=""):
        self.tracelevel = mylevel
        self.traceproduction = (getenv("TRACE_PRODUCTION", "NO") == "YES")
        try:
            self.tracelevel = int(getenv("TRACE_LEVEL", mylevel))
        except ValueError:      # If not integer, take default.
            pass
        self.tracetarget = mytarget
        try:
            self.tracetarget = int(getenv("TRACE_TARGET", mytarget))
        except ValueError:      # If not integer, take default.
            pass
        self.tracefile = getenv("TRACE_FILE", myfile)
        self.tracefacil = getenv("TRACE_FACIL", myfacil).upper()
        if not self.traceproduction:
            if self.tracelevel > 0:
                self.trace(1,"DEBUG info level %s targets %s facil %s" 
                    % (self.tracelevel,self.tracetarget,self.tracefacil) )

# i s P r o d u c t i o n 
    def isProduction(self):
        return self.traceproduction

# n t r a c e     trace with no identified facility name.
    # Old style, calls new style.
    def trace(self, level, line):
        self.ntrace(level, line)

    def ntrace(self, level, line):
        # If not in production mode or yes in production mode with level==0.
        if (not (getenv("TRACE_PRODUCTION", "NO") == "YES")
            or level == 0
            ):
            # If we are tracing at a high enough level to include this item, 
            #  then send it to the appropriate target(s).
            if level <= self.tracelevel:
                # Get a timestamp
                self.vecT = localtime()
                (yr,mo,da,hr,min,sec,x,y,z) = self.vecT
                self.ascT = "%4d%02d%02d_%02d%02d%02d" % (yr,mo,da,hr,min,sec)
                #linestart = ascT + " " + "%1d"%level + " "
                self.linestart = "%s %1d %-4s " % (self.ascT,level,"    ")
                
                # If console only, or console and others, print to stdout.
                if (((self.tracetarget & 1) and not (self.tracetarget & 2)) 
                  or not (self.tracetarget & 6)):
                    print self.linestart + " " + line
                
                # If HTML format, add line break.
                if (self.tracetarget & 2):
                    print "<br>" + self.linestart + " " + line
                
                # Or append to trace file.
                if (self.tracetarget & 4):
                    self.fWriteCarefully(self.tracefile, 'a', 
                        self.linestart+" "+line, 5)
        else:       # If in production mode and level > 0
            pass    #  go away.

# n t r a c e f   trace associated with a named facility.
    # Old style, calls new style.
    def tracef(self, level, facility, line):
        self.ntracef(level, facility, line)

    def ntracef(self, level, facility, line):
        # If not in production mode or yes in production mode with level==0.
        if (not (getenv("TRACE_PRODUCTION", "NO") == "YES")
            or level == 0
            ):
            # If we are tracing at a high enough level to include this item, 
            #  then send it to the appropriate target(s).
            if level <= self.tracelevel:
                # Now assess the facility: include Y or N?
                self.facilcaps = facility.upper()
                # If NONE, then the answer is probably No.  
                if self.tracefacil.find("NONE") >= 0:
                    self.traceme = False
                # If ALL or mentioned explicitly, then the answer is probably Yes.  
                if (self.tracefacil == "" 
                or  self.tracefacil.find(self.facilcaps) >= 0 
                or  self.tracefacil.find("ALL") >= 0):
                    self.traceme = True
                # If explicitly excluded, then the answer is definitely No.  
                if self.tracefacil.find(("-"+self.facilcaps)) >= 0:
                    self.traceme = False
                if self.traceme:
                    # Get a timestamp
                    self.vecT = localtime()
                    (self.yr,self.mo,self.da,self.hr,self.min,self.sec,
                        self.x,self.y,self.z) = self.vecT
                    self.ascT = ("%4d%02d%02d_%02d%02d%02d" 
                        % (self.yr,self.mo,self.da,self.hr,self.min,self.sec))
                    self.linestart = "%s %1d %-4s " % (self.ascT,level,facility)
                    # If console only, or console and others, print to stdout.
                    if (((self.tracetarget & 1) and not (self.tracetarget & 2)) 
                        or not (self.tracetarget & 6)):
                        print self.linestart + " " + line
                    
                    # If HTML format, add line break.
                    if (self.tracetarget & 2):
                        print "<br>" + self.linestart + " " + line
                    
                    # Or append to trace file.
                    if (self.tracetarget & 4):
                        self.fWriteCarefully(self.tracefile, 'a', 
                            self.linestart+" "+line, 10)
        else:       # If in production mode and level > 0
            pass    #  go away.

# f W r i t e C a r e f u l l y         write to file avoiding file-busy errors.
    def fWriteCarefully(self, outfile, mode, outline, retries):
        # Careful: if the file is still busy with the last write, 
        #  wait a second and try it again.  A few times.
        #  Yes, this actually happens disturbingly frequently.
        for idxErrorCount in range(retries+1):
            try:
                with open(outfile, mode) as f:
                    if idxErrorCount == 0:
                        f.write(outline + "\n")
                    else:
                        outline += " filebusyretries|%s|"%(idxErrorCount)
                        f.write(outline + "\n")
                    #f.flush()
                    #f.close()
                break                   # Leaves the for loop.
            except IOError, e:
                sleep(1)
        # If we can't write after several retries, tough.  


# D e c o r a t o r s 

# Plain decorator, no facility code.  Logs entry and exit.  

# NEW VERSION @ntrace
if (getenv("TRACE_PRODUCTION", "NO") == "YES"):
    def ntrace(func):
        return func
else:
    def ntrace(func):
        @wraps(func)
        def wrap2(*args,**kwargs):
            NTRC.ntrace(1,"entr %s args=%s,kw=%s" % (func.__name__,args,kwargs))
            result = func(*args,**kwargs)
            NTRC.ntrace(2,"exit %s result|%s|" % (func.func_name,result))
            return result
        return wrap2

# OLD VERSION @trace
if (getenv("TRACE_PRODUCTION", "NO") == "YES"):
    def trace(func):
        return func
else:
    def trace(func):
        def wrap2(*args,**kwargs):
            TRC.trace(1,"entr %s args=%s,kw=%s" % (func.__name__,args,kwargs))
            result = func(*args,**kwargs)
            TRC.trace(2,"exit %s result|%s|" % (func.func_name,result))
            return result
        wrap2.func_name = func.func_name
        return wrap2

# Decorator with facility code and priority level.  
# Facility code may be left blank to use priority or "self" printing.

# NEW VERSION @ntracef
if (getenv("TRACE_PRODUCTION", "NO") == "YES"):
    def ntracef(facil="",level=1):
        def tracefinner(func):
            return func
        return tracefinner
else:
    def ntracef(facil="",level=1):
        def tracefinner(func):
            @wraps(func)
            def wrap1(*args,**kwargs):
                if len(args)>0 and str(type(args[0])).find("class") >= 0:
                    _id = getattr(args[0],"ID","")
                    NTRC.ntracef(level,facil,"entr %s args=<%s id=|%s|> |%s| kw=%s" 
                        % (func.__name__,args[0].__class__.__name__,_id,
                        args[1:],kwargs))
                else:
                    NTRC.ntracef(level,facil,"entr %s args=%s,kw=%s" 
                        % (func.__name__,args,kwargs))
                result = func(*args,**kwargs)
                if len(args)>0 and str(type(args[0])).find("class") >= 0:
                    _id = getattr(args[0],"ID","")
                    NTRC.ntracef(level,facil,"exit %s <%s id=|%s|> result|%s|" 
                        % (func.func_name,args[0].__class__.__name__,_id,result))
                else:
                    NTRC.ntracef(level,facil,"exit %s result|%s|" % (func.func_name,result))
                return result
            return wrap1
        return tracefinner

# OLD VERSION @tracef
if (getenv("TRACE_PRODUCTION", "NO") == "YES"):
    def tracef(facil="",level=1):
        def tracefinner(func):
            return func
        return tracefinner
else:
    def tracef(facil="",level=1):
        def tracefinner(func):
            def wrap1(*args,**kwargs):
                if len(args)>0 and str(type(args[0])).find("class") >= 0:
                    _id = getattr(args[0],"ID","")
                    TRC.tracef(level,facil,"entr %s args=<%s id=|%s|> |%s| kw=%s" % (func.__name__,args[0].__class__.__name__,_id,args[1:],kwargs))
                else:
                    TRC.tracef(level,facil,"entr %s args=%s,kw=%s" 
                        % (func.__name__,args,kwargs))
                result = func(*args,**kwargs)
                if len(args)>0 and str(type(args[0])).find("class") >= 0:
                    _id = getattr(args[0],"ID","")
                    TRC.tracef(level,facil,"exit %s <%s id=|%s|> result|%s|" 
                        % (func.func_name,args[0].__class__.__name__,_id,result))
                else:
                    TRC.tracef(level,facil,"exit %s result|%s|" 
                        % (func.func_name,result))
                return result
            wrap1.func_name = func.func_name
            return wrap1
        return tracefinner

# T R C  i n s t a n c e 

''' Easy usage:

    Now, for the convenience of the lazy, populate a 
     globally accessible instance that can be used with
     no further action required.
    If the user really wants a particular facility name, 
     make another instance or use setFacility.
    
    Simplest way:
        from NewTraceFac import NTRC,ntrace,ntracef
    then
        @ntracef("NAME")         # or just "trace" if no facility code
        def somefunction()
    and
        NTRC.ntracef(3,"NAME","string with %s substitution%s"%("two","s"))
                                # or just "ntrace" if no facility code

    Since the function decorators use the strings "entr" and "exit" 
     between the facility name and the function name, it is recommended
     that one use some other four letter codes in the traced lines, 
     such as "proc" so that successive lines line up into clear columns.
'''
# NEW VERSION NTRC
NTRC = CNewTrace()
# OLD VERSION TRC
TRC = CNewTrace()

# Edit history:
# 20141020  RBL Add fWriteCarefully routine to minimize problems with 
#                file-busy contention, which sometimes happens.
#                CHKNET suffers a lot of this type of error.
# 20150112  RBL Because of heat from various members of the Python
#                community about the use of the name "trace", I 
#                will change the name to "ntrace".  After some 
#                searching on Google, one finds that the name 
#                "rtrace" was already used for ray tracing, 
#                "dtrace" for some sort of debugging, and
#                "dbtrace" for some database debugging; but 
#                "ntrace" was relatively unused, appears only as
#                a variable name in a few places.  Voila!
#               Begin to add name changes: trace -> ntrace and 
#                all its relatives, ntrace(), ntracef(), and their
#                decorators, and TRC instance.  
# 20160921  RBL Begin to wean the code from the old "trace" to the 
#                new "ntrace" and from "TRC" to "NTRC".  Make those
#                new names the default call, so that they are the 
#                slightly faster versions.  
#               Clean up some of the longer-than-80 lines.
# 20170127  RBL V13: Add PRODUCTION versions of functions and decorators
#                that do as little as possible to reduce CPU burden
#                completely without editing any code; just set a 
#                new environment variable TRACE_PRODUCTION=YES and
#                poof, all the code goes away.  
#                Well, not all, exactly.  Have to honor traces at 
#                level zero, even in production mode, because they
#                are often important informational messages.  
#                (And optimize the tests for speed.)
# 20170129  RBL V14: Add method to tell if production mode is turned on
#                so that users can report it.  
# 
# 

#END
