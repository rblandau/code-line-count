#!/usr/bin/python
# NewCodeLineCounts.py
# Adapted from old CodeLineCounts.pl used for years around 20030321,
#  which in turn came from old old really old Perl version years before that. 

''' 
Count lines of code and other stuff in a file.  
Counts
- total lines
- comment lines:    single lines or blocks, for languages that have blocks
- blank lines
- short lines:      like lone braces on code blocks, for C, Java, PHP, et al.
- code lines:       whatever isn't blank, comment, or short

Emits a single line of output, tab-separated: name, type, and counters: 
filename    filetype    total   code    comment blank   short
The filetype is a group name based on the file extension.  

Impending change of philosophy: do the normal cases, screw the edge cases.  
E.g., anything that isn't blank or pure comment is code.

New version: uses polymorphic classes to examine language lines.
'''

from NewTraceFac import NTRC,ntrace,ntracef
import re
import sys
import os
from abc import ABCMeta, abstractmethod


#===========================================================
# c l a s s   C A n a l y z e L a n g u a g e L i n e s s  parent base class
class CAnalyzeLanguageLines(object):
    '''
    Parent skeleton class to parse comments within file types.  
    
    Subclass this and implement whatever methods are necessary for that
     particular language.  E.g., if a language does not have block
     comments, then don't bother to implement anything to look for them.
     Every prototype function returns False (with pass) if not implemented.
     NOTE: Every subclass must implement HashCommentOnly and CodePlusComment.
     
    The functions must be stateless, because they may be optimized
     away by boolean expressions (and, or).
    '''
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @ntrace
    def bIsBlank(self, mysLine):
        ''' Does line contain only white space? '''
        return(tf(re.match("^\s*\r?$", mysLine)))

    @abstractmethod
    def bIsHashCommentOnly(self, mysLine):
        ''' Does line contain only a comment and no code? '''
        pass

    @abstractmethod
    def bIsCodePlusComment(self, mysLine):
        ''' Does line contain code plus a comment at the end of it? '''
        pass

    def bIsCommentBlockBegin(self, mysLine):
        ''' Does line begin a comment block? '''
        pass

    def bIsCommentBlockEnd(self, mysLine):
        ''' Does line terminate a comment block? '''
        pass

    def bIsCommentBlockBeginOrEnd(self, mysLine):
        ''' Ambiguous introducer/terminator for comment block? '''
        pass

    def bIsShort(self,mysLine):
        ''' Is line very short, e.g., a single brace? '''
        pass


#===========================================================
# C l a s s   C G   o f   g l o b a l   d a t a 
class CG(object):
    
    cLang = 'vvvvvvvv'      # Pointer to language-specific instance.
    sProcessedAs = ""       # What type of language do we think it is?

    bShort = 0
    bBlank = 0
    bHashCommentOnly = 0    # Comment on this line.  
    bCommentBlockBegin = 0  # Beginning of a block comment.
    bCommentBlockEnd = 0    # End of block comment.
    bCommentBlockAmbiguous = 0  # Python only: maybe begin or end.
    bForceComment = 0       # Force this line to be considered a comment.
    
    bInCommentRegion = 0        # Inside a block comment.
    bInCommentRegionNext = 0    # Maybe transition to anew state.  

    # Counters for types of lines.
    nLines = 0
    nBlank = 0
    nShort = 0
    nComment = 0
    nCode = 0

    @ntrace
    def fnvResetFlags(self):
        bBlank = bShort = 0
        bHashCommentOnly = 0
        bCommentBlockBegin = 0
        bCommentBlockEnd = 0
        bCommentBlockAmbiguous = 0
        bForceComment = 0

    # Return counters, some or all.  
    def getAll(self):
        return (self.nLines, self.nCode, self.nBlank, 
            self.nShort, self.nComment)

    def getLines(self):
        return self.nLines


#===========================================================
# Subclasses to parse specific language groups.

#===========================================================
# C P Y T H O N 
class CPython(CAnalyzeLanguageLines):

    @ntrace
    def bIsHashCommentOnly(self, mysLine):
        return(tf(re.match("^\s*#.*$", mysLine)))

    @ntrace
    def bIsCodePlusComment(self, mysLine):
        return(tf(re.match("^\s*\S+.*#.*$", mysLine)))

    '''
    Python has this abominable business of 
    (1) beginning and ending block comments with the same string, 
    (2) having *two* versions of the block comment strings, and
    (3) permitting the two types of block comments to *nest*, yikes.
    This makes figuring out what is inside and outside a block 
     comment very tricky.  
    Nested block comments, using the two types of quotes, are
     currently mis-handled here.  Tough.  Rare case.
     If you want to fix it so that comment blocks can nest, 
     knock yourself out.  
    The code here fudges the possibility of code plus what looks like 
     a block comment on the same line.  
     If there is any text outside the 
     comment delimiter, then the line is code; otherwise it is 
     inside a comment.  Maybe you could convince me to fix this.  

    And then there are the abominable -- but, sadly, useful -- 
        if False:<opening triplequote>
        code to be commented out
        <closing triplequote>
     which should count as code, comment, comment;
                and
        <opening triplequote>
        code to be commented out
        <closing triplequote> and False
     which should counta as comment, comment, code.
    What a crock.

    Here's what it *should* conclude:
  
    whitespace only                         blank if not in comment region
    non-whitespace only                     code
    whitespace hash anything                single-line comment
    non-whitespace hash anything            code
    whitespace triplequote whitespace       begin or end (xor) comment region
    whitespace triplequote non-whitespace   comment & begin comment region
    non-whitespace triplequote whitespace   comment & end comment region if in,
                                            or code & begin comment region
    anything-includingblank-whileincommentregion
                                            comment
    whitespace triplequote anything triplequote whitespace
                                            single-line comment
    
    Now let's see if I can make this stupid code do that.  
    '''
    @ntrace
    def bIsApost(self, mysLine):
        ''' Just three apostrophes? '''
        return(tf(re.match("^(\s*)\'\'\'(\s*)$", mysLine)))
        
    @ntrace
    def bIsCommentBlockBeginApost(self, mysLine):
        ''' Does comment block start with three apostrophes? '''
        return(tf(re.match("^\s*\'\'\'(\s*\S+.*)$", mysLine)))
        
    @ntrace
    def bIsCommentBlockEndApost(self, mysLine):
        return(tf(re.match("^(\s*\S+.*)\'\'\'\s*$", mysLine)))

    @ntrace
    def bIsQuote(self, mysLine):
        ''' Just three apostrophes? '''
        return(tf(re.match("^(\s*)\"\"\"(\s*)$", mysLine)))
        
    @ntrace
    def bIsCommentBlockBeginQuote(self, mysLine):
        ''' Does comment block begin with three double quotes? '''
        return(tf(re.match("^\s*\"\"\"(\s*\S+.*)$", mysLine)))

    @ntrace
    def bIsCommentBlockEndQuote(self, mysLine):
        return(tf(re.match("^(\s*\S+.*)\"\"\"\s*$", mysLine)))

    @ntrace
    def bIsCommentBlockBeginOrEnd(self, mysLine):
        return(self.bIsApost(mysLine)
            or self.bIsQuote(mysLine))

    @ntrace
    def bIsCommentBlockBegin(self, mysLine):
        ''' A comment block can use either form of quotes. '''
        return(self.bIsCommentBlockBeginApost(mysLine) 
            or self.bIsCommentBlockBeginQuote(mysLine))
            
    @ntrace
    def bIsCommentBlockEnd(self, mysLine):
        return(self.bIsCommentBlockEndApost(mysLine) 
            or self.bIsCommentBlockEndQuote(mysLine))


#===========================================================
# P E R L   A W K   S H   R   M A K   S E D   P R O P E R T I E S 
class CPerlAwkShR(CAnalyzeLanguageLines):
    '''
    Languages that have only single line comments that start with #
    '''

    @ntrace
    def bIsHashCommentOnly(self, mysLine):
        return(tf(re.match("^\s*#.*$",mysLine)))

    @ntrace
    def bIsCodePlusComment(self, mysLine):
        return(tf(re.match("^\s*\S+.*#.*$",mysLine)))


#===========================================================
# C   C P P   J A V A S C R I P T   J A V A   S C A L A 
class CCCppJsJava(CAnalyzeLanguageLines):
    '''
    Languages that have block comments delimited by  /* ... */
     and single line comments starting with  //
     Yes, this is a little too generous for vanilla C and H.
    '''

    @ntrace
    def bIsHashCommentOnly(self, mysLine):
        return(tf(re.match("^\s*\/\/.*$",mysLine)))

    @ntrace
    def bIsCodePlusComment(self, mysLine):
        return(tf(re.match("^\s*\S+.*\/\/.*$",mysLine)))

    @ntrace
    def bIsCommentBlockBegin(self, mysLine):
        return(tf(re.match("^\s*\/\*.*$",mysLine)))

    @ntrace
    def bIsCommentBlockEnd(self, mysLine):
        return(tf(re.match("^.*\*\/\s*$",mysLine)))

    @ntrace
    def bIsShort(self, mysLine):
        return(tf(re.match("^\s*(\{|\})\s*$", mysLine)))


#===========================================================
# X M L   H T M L   X S L   e t  a l .
class CXmlHtml(CAnalyzeLanguageLines):
    ''' 
    XML-like languages that use block comments with <!-- ... -->
    '''

    @ntrace
    def bIsHashCommentOnly(self, mysLine):
        return 0

    @ntrace
    def bIsCodePlusComment(self, mysLine):
        return(tf(re.match("^\s*\S+.*\<!.*$",mysLine)))

    @ntrace
    def bIsCommentBlockBegin(self, mysLine):
        return(tf(re.match("^\s*\<!--.*$",mysLine)))

    @ntrace
    def bIsCommentBlockEnd(self, mysLine):
        return(tf(re.match("^.*--\>\s*$",mysLine)))


#===========================================================
# B A T   C M D 
class CBatCmd(CAnalyzeLanguageLines):
    '''
    Window/DOS/NT .bat and .cmd files that use REM as comment introducer.
    '''

    @ntrace
    def bIsHashCommentOnly(self, mysLine):
        return(tf(re.match("^\s*(REM|rem).*$",mysLine)))

    @ntrace
    def bIsCodePlusComment(self, mysLine):
        return 0                # Not possible in BAT files.


#===========================================================
# I N I 
class CIni(CAnalyzeLanguageLines):
    '''
    This permits lots and lots of different styles of comments.  
     Windows (and other) INI files permit # and sometimes ! for comments; 
     and PHP takes semicolon; and Visual Studio and other Windows programs 
     take semicolon and sometimes // and Latex takes %.  
     And Visual Studio and some other Windows utilities permit 
     C++-style line and block comments, too.  
     Ah, consistency.  What a swamp.
    Most of these things should appear at the beginning of a line anyway, 
     so if it even vaguely resembles a comment, it probably is; otherwise code.
    '''

    @ntrace
    def bIsHashCommentOnly(self, mysLine):
        return(tf(re.match("^\s*(#|!|;|%|\/\/).*$",mysLine)))

    @ntrace
    def bIsCodePlusComment(self, mysLine):
        return 0

    @ntrace
    def bIsCommentBlockBegin(self, mysLine):
        return(tf(re.match("^\s*\/\*.*$",mysLine)))

    @ntrace
    def bIsCommentBlockEnd(self, mysLine):
        return(tf(re.match("^.*\*\/\s*$",mysLine)))


#===========================================================
# T E X T 
class CText(CAnalyzeLanguageLines):
    '''
    Catch-all class to use if we don't recognize the specific file type.
    Text is just characters and maybe blank lines.
    '''
    
    @ntrace
    def bIsHashCommentOnly(self,mysLine):
        return 0                # No comments in text files.

    @ntrace
    def bIsCodePlusComment(self,mysLine):
        return 0                # No comments in text files.


#===========================================================
# f n P r o c e s s F i l e 
@ntrace
def fnProcessFile(mysFilename,mysFiletype):
    '''
    Process the file line by line.

    We already know the file has been checked for existence.

    Send each line of the file to function for analysis, 
     then assign the line to a category based on what 
     was found.
    '''
    with open(mysFilename, "r") as fhInput:
        for sLine in fhInput:
            fnProcessLine(sLine,mysFiletype)

            # Determine type of line and increment count.
            g.nLines += 1
            
            # A blank is a blank is a blank: white space with no content.
            #  Unless it's inside a block comment.
            if g.bBlank and not g.bInCommentRegion: 
                g.nBlank += 1

            '''
            What we want here is

            block comments have to work for these cases:

                in C and friends:
            code? /*
            code? /* stuff
            stuff */ code?
            */ code?
            code? /* stuff */ code?
                
                and in Python:
            code? """
            code? """ stuff
            stuff """ code? 
            """ code? 
            code? """ stuff """
            """ stuff """ code? 

            This is not simple.

            '''

            # Hash comment or 
            #  block comment that begins and ends on the same line.
            if (g.bHashCommentOnly and not g.bInCommentRegion): 
                g.nComment += 1
            
            # Inside a block comment region.
            if (g.bInCommentRegion or g.bForceComment): 
                g.nComment += 1

            # Count short lines separately from longer code lines. 
            if g.bShort:
                g.nShort += 1

            # If not special, then code.  (keep running tally)
            g.nCode = g.nLines - g.nBlank - g.nComment - g.nShort
            NTRC.ntrace(3,"proc afterline lines|%s| code|%s| comment|%s| "
                "blank|%s| short|%s| inblock|%s|" 
                % (g.nLines, g.nCode, g.nComment, g.nBlank, g.nShort, 
                g.bInCommentRegion))

            # Advance the block comment state.  
            g.bInCommentRegion = g.bInCommentRegionNext


#===========================================================
# f n P r o c e s s L i n e 
@ntrace
def fnProcessLine(mysLine,mysFiletype):
    '''
    Process one line of the file.
    
    Call each routine in turn to look for special sequences on the line, 
     and note the results in a bunch of booleans.
    '''
    g.fnvResetFlags()
    g.bBlank = g.cLang.bIsBlank(mysLine)
    g.bHashCommentOnly = g.cLang.bIsHashCommentOnly(mysLine)
    g.bCodePlusComment = g.cLang.bIsCodePlusComment(mysLine)
    g.bCommentBlockBegin = g.cLang.bIsCommentBlockBegin(mysLine)
    g.bCommentBlockEnd = g.cLang.bIsCommentBlockEnd(mysLine)
    g.bCommentBlockAmbiguous = g.cLang.bIsCommentBlockBeginOrEnd(mysLine)
    g.bShort = g.cLang.bIsShort(mysLine)
    # TEMP
    g.bForceComment = 0
    # END TEMP
    NTRC.ntrace(3, "proc linetype1 blank|%s| commonly|%s| codeplus|%s| "
        "blkbegin|%s| blkend|%s| blkambig|%s| forcecomm|%s|" 
        % (g.bBlank, g.bHashCommentOnly, g.bCodePlusComment, 
        g.bCommentBlockBegin, g.bCommentBlockEnd, g.bCommentBlockAmbiguous, 
        g.bForceComment))

    g.bInCommentRegionNext = g.bInCommentRegion
    if g.bCommentBlockBegin:
        g.bInCommentRegionNext = 1
        if not g.bCommentBlockEnd:
            g.bForceComment = 1
    if g.bCommentBlockEnd:      # May be code before begin but looks like end.
        g.bInCommentRegionNext ^= 1
    if g.bCommentBlockAmbiguous:
        g.bInCommentRegionNext ^= 1 # Toggle (xor) from in to out or v-v.  
        g.bForceComment = 1     # Ambiguous but a comment at begin or end.
    if g.bCommentBlockBegin and g.bCommentBlockEnd and not g.bCodePlusComment:
        g.bHashCommentOnly = 1

    NTRC.ntrace(3,"proc linetype2 regionprev|%s| regionnext|%s| "
        "commonly|%s| forcecomment|%s| ambig|%s|" 
        % (g.bInCommentRegion, g.bInCommentRegionNext, g.bHashCommentOnly, 
        g.bForceComment, g.bCommentBlockAmbiguous))
    return mysLine.strip()

# t f 
# Reduce match objects or None to one and zero, for brevity.  
def tf(something):
    if something:
        return 1
    else:
        return 0

#===========================================================
# M A I N 
@ntrace
def main(mysFilename,mysType):
    '''
    Main line: choose proper processor for the file type, 
     process the file, print results.
    '''

    # Mucho stupid factory to get the right class to analyze this file.
    if (re.match("^(c|cpp|h|hpp|js|java|scala)$",mysType,re.I) ):
        g.cLang = CCCppJsJava()
        g.sProcessedAs = 'cpp/js/java'
    elif (re.match("^(pl|awk|r|sh|ksh|csv|mak|sed|properties)$",mysType,re.I)):
        g.cLang = CPerlAwkShR()
        g.sProcessedAs = 'sh/perl/r'
    elif (re.match("^(py|pm)$",mysType,re.I)):
        g.cLang = CPython()
        g.sProcessedAs = 'python'
    elif (re.match("^(xsl|xml|htm|html|xhtml|tpl|j2)$",mysType,re.I)):
        g.cLang = CXmlHtml()
        g.sProcessedAs = 'xml/html'
    elif (re.match("^(bat|cmd)$",mysType,re.I)):
        g.cLang = CBatCmd()
        g.sProcessedAs = 'bat'
    elif (re.match("^(ini)$",mysType,re.I)):
        g.cLang = CIni()
        g.sProcessedAs = 'ini'
    else:
        g.cLang = CText()
        g.sProcessedAs = 'text'

    NTRC.ntrace(3,"proc main assigned filetype|%s| class|%s|" 
        % (mysType, g.cLang))
    fnProcessFile(sFilename,sFileext)   # Do all this crap to the file.
    NTRC.ntrace(3,"proc main afterfile lines|%s| code|%s| "
        "blank|%s| short|%s| comment|%s|" 
        % (g.getAll()))

    # The conservative way to calculate code lines is to remove 
    # everything that we saw that absolutely is not a line of code.
    # Blanks and comment-only lines are not code for sure.  
    # Short lines are arguable, so we report them separately.  
    (total,zerocode,blank,short,comment) = g.getAll()
    g.nCode = total - blank - short - comment   # Code is what's left over.
    # Finally, the single line of output for this file.  
    print "%s\t%s\t%d\t%d\t%d\t%d\t%d" % \
    (sFilename,g.sProcessedAs,total,g.nCode,comment,blank,short)

    return 0


#===========================================================
#   E N T R Y   P O I N T 
if __name__ == "__main__":
    '''
    Entry point: check arguments, maybe print usage message if no file named.
     Check to see that file exists and is not just a directory.
    '''

    if len(sys.argv) <= 1:
        print "Usage: python {}  <input-filespec>".format(sys.argv[0])
        print "       Line out = filename, filetype, total, code, comment, blank, short"
        print "       Output one line to stdout."
        exit(1)

    sFilename = sys.argv[1]
    # Careful to ignore directories and typos; process real files only.
    if not os.path.isdir(sFilename):
        if not os.path.isfile(sFilename):
            raise IOError("Input file not found: \"{}\"".format(sFilename))
        else:
            (_, sFileextplusdot) = os.path.splitext(sFilename)
            sFileext = sFileextplusdot.lstrip('.')
            NTRC.tracef(3,"MAIN","proc fname|%s| ext|%s|" 
                % (sFilename,sFileext))

            # Instantiate all the global data, flags and counters.
            g = CG()
            sys.exit(main(sFilename, sFileext))


# Edit history:
# 1996xxxx  RBL Stone axe Perl versions used at DEC.
# 2001xxxx  RBL Neolithic Perl versions for personal use.
# 20030321  RBL Merely ancient Perl version used at Dell.
# 20140324  RBL Moldy, old Python version for my use.  
# 20170522  RBL New Python version, derived from old Python version,
#                which was derived from really ancient Perl version.  
#               If you think this is bad, you should have seen 
#                the old Python version, that worked but was ugly,
#                an if-elif statement that went on for three pages.
#                And you wouldn't believe the spaghetti swamp 
#                that the original Perl code was.  
# 20170609  RBL Fix all the regexes and logic for block comments.  
#                Boy, do I hate that style of block comment (introducer 
#                and terminator the same string, and nesting, shudder).  
#                Still a mess and still does not cover all cases, e.g.,
#                nested ''' within """ and v-v.
# 
# 

# END
