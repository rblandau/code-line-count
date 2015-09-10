#!/usr/bin/python
# CodeLineCounts.py
#                                   Rick Landau 20140324
# Adapted from old CodeLineCounts.pl used for years at Dell from 20030321,
#  which in turn came from old old Perl version years before that. 
#                                   Minor update 20150102
# 

''' Count lines of code and other stuff in a file.  

    Impending change of philosophy: do the normal cases, 
    screw the edge cases.  
'''

from NewTraceFac import TRC,trace,tracef
import re
from sys import argv

@tracef("LINE")
def fnProcessLine(mysLine,mysType):
        
    TRC.trace(3,"proc ProcessLine1 lines|%s| code|%s| blank|%s| short|%s| comment|%s|" % (g.getAll()))

    # A blank line is blank in any language.
    if ( re.match("^\s*\r?$",mysLine) ):
        g.incBlank()

# P H A S E   1 :   L O O K   F O R   S E Q U E N C E S 
    # Test the line in language-specific ways.  
    # As ugly and complex as all this looks, it works only 
    # for pretty vanilla cases.  It is still too simple
    # to get a correct answer in all cases.  
# C   C P P   H   H P P   J A V A   S C A L A 
    if ( re.match("^(c|cpp|h|hpp|java|scala)$",mysType,re.I) ):
        TRC.trace(5,"proc match line as C, Java, or Scala")
        g.bCommentOnly = re.match("^\s*(\/\*.*\*\/|\/\/.*)\s*$",mysLine)
        g.bCommentBegin = re.match("^.*(\/\*|\/\/).*$",mysLine)
        g.bCommentEnd = re.match("^.*(\*\/|\/\/).*$",mysLine)
        if ( g.bCommentBegin ):
            g.bCodeCommentBegin = re.match("^\s*\S+.*(\/\*|\/\/).*$",mysLine)
# S H   K S H 
    elif ( re.match("^(sh|ksh)$",mysType,re.I) ):
        TRC.trace(5,"proc match line as Shell script")
        g.bCommentOnly = re.match("^\s*#.*\s*$",mysLine)
        g.bCommentBegin = re.match("^.*#.*$",mysLine)
        g.bCommentEnd = re.match("^.*#.*$",mysLine)
        if ( g.bCommentBegin ):
            g.bCodeCommentBegin = re.match("^\s*\S+.*(#).*$",mysLine)
        TRC.trace(3,"proc  s=|%s|%s| type=|%s| blank=|%s| short=|%s| commentonly=|%s| commentbegin=|%s| commentend=|%s| codebegin=|%s|" % (g.nLines, mysLine, mysType, g.bBlank, g.bShort, g.bCommentOnly, g.bCommentBegin, g.bCommentEnd, g.bCodeCommentBegin))
# P E R L   A W K   R
    elif ( re.match("^(pl|awk|r)$",mysType,re.I) ):
        TRC.trace(5,"proc match line as Perl or Awk")
        g.bCommentOnly = re.match("^\s*#.*\s*$",mysLine)
        g.bCommentBegin = re.match("^.*#.*$",mysLine)
        g.bCommentEnd = re.match("^.*#.*$",mysLine)
        if ( g.bCommentBegin ):
            g.bCodeCommentBegin = re.match("^\s*\S+.*(#).*$",mysLine)
# P Y T H O N 
    elif ( re.match("^(py|pm)$",mysType,re.I) ):
        TRC.trace(5,"proc match line as Python")
        g.bShort = 0
        g.bCommentOnly = re.match("^\s*#.*\s*$",mysLine)
        g.bCommentBegin = re.match("^.*#.*$",mysLine)
        g.bCommentEnd = re.match("^.*#.*$",mysLine)
        if ( g.bCommentBegin ):
            g.bCodeCommentBegin = re.match("^\s*\S+.*(#).*$",mysLine)
        TRC.trace(5,"proc hashcomment only|%s| begin|%s| end|%s|" % (tf(g.bCommentOnly),tf(g.bCommentBegin),tf(g.bCommentEnd)))

        # E x p e r i m e n t a l :  try to find block comments in Python.  
        # Makes me crazy to deal with apostrophe and quote both.
        # Beginning or ending of block comment?
        g.bCommentBlockAloneApost = re.match("^\s*(\'{3})\s*$",mysLine)
        g.bCommentBlockAloneQuote = re.match("^\s*(\"{3})\s*$",mysLine)

        # Comment with non-blank text before or after the triple-thing?
        # All of these are wrong, I know.  Any code on the
        # same line could innocently contain apostrophes or quotes.
        g.bCommentBlockTextAfterApost = re.match("^\s*(\'{3}).*[^\s\']+.*$",mysLine)
        g.bCommentBlockTextAfterQuote = re.match("^\s*(\"{3}).*[^\s\"]+.*$",mysLine)
        g.bCommentBlockTextBeforeApost = re.match("^.*[^\s\']+.*(\'{3})\s*$",mysLine)
        g.bCommentBlockTextBeforeQuote = re.match("^.*[^\s\"]+.*(\"{3})\s*$",mysLine)
        g.bCommentBlockTextBothApost = re.match("^\s*\S+.*(\'{3})\s*\S+.*$",mysLine)
        g.bCommentBlockTextBothQuote = re.match("^\s*\S+.*(\"{3})\s*\S+.*$",mysLine)

        # Does block comment begin and end on the same line?
        g.bCommentBlockSingleApost = re.match("^\s*(\'{3})[^\']*(\'{3})\s*$",mysLine)
        g.bCommentBlockSingleQuote = re.match("^\s*(\"{3})[^\']*(\"{3})\s*$",mysLine)

        # How many block comments on this line?  
        # (Why would I care?)
        mIntrosApost = re.findall("(\'{3})",mysLine)
        g.nCommentIntroCountApost = len( mIntrosApost ) % 2
        mIntrosQuote = re.findall("(\"{3})",mysLine)
        g.nCommentIntroCountQuote = len( mIntrosQuote ) % 2

        TRC.trace(5,"proc singlequote pyblock1 alone|%s| txtafter|%s| txtbefore|%s| txtboth|%s| single|%s| count|%s| inblock|%s|" % (tf(g.bCommentBlockAloneApost),tf(g.bCommentBlockTextAfterApost),tf(g.bCommentBlockTextBeforeApost),tf(g.bCommentBlockTextBothApost),tf(g.bCommentBlockSingleApost),g.nCommentIntroCountApost,g.bInCommentRegionApost))
        TRC.trace(5,"proc doublequote pyblock1 alone|%s| txtafter|%s| txtbefore|%s| txtboth|%s| single|%s| count|%s| inblock|%s|" % (tf(g.bCommentBlockAloneQuote),tf(g.bCommentBlockTextAfterQuote),tf(g.bCommentBlockTextBeforeQuote),tf(g.bCommentBlockTextBothQuote),tf(g.bCommentBlockSingleQuote),g.nCommentIntroCountQuote,g.bInCommentRegionQuote))
        # E n d   o f   e x p e r i m e n t a l   j u n k . 

# X M L   X S L   H T M   H T M L   X H T M L 
    elif ( re.match("^(xsl|xml|htm|html)$",mysType,re.I) ):
        TRC.trace(5,"proc match line as XML or HTML")
        g.bShort =        0
        g.bCommentOnly = re.match("^\s*\<!--.*--\>\s*$",mysLine)
        g.bCommentBegin = re.match("^.*(<!--).*$",mysLine)
        g.bCommentEnd = re.match("^.*(-->).*$",mysLine)
        if ( g.bCommentBegin ):
            g.bCodeCommentBegin = re.match("^\s*(\S+.*)(<!--).*$",mysLine)
# B A T   C M D 
    elif ( re.match("^(bat|cmd)$",mysType,re.I) ):
        TRC.trace(5,"proc match line as Batch script")
        g.bShort =        0
        g.bCommentOnly = re.match("^\s*REM.*$",mysLine)
        g.bCommentBegin = re.match("^\s*REM.*$",mysLine)
        g.bCommentEnd = re.match("^\s*REM.*$",mysLine)
        g.bCodeCommentBegin = 0
# M A K 
    elif ( re.match("^(mak)$",mysType,re.I) ):
        TRC.trace(5,"proc match line as makefile")
        g.bShort =        0
        g.bCommentOnly = re.match("^\s*#.*$",mysLine)
        g.bCommentBegin = re.match("^[^\t].*[^\\]#.*$",mysLine)
        g.bCommentEnd = re.match("^.*[^\\]#.*$",mysLine)
        if ( g.bCommentBegin ):
            g.bCodeCommentBegin = re.match("^\s*\S+.*([^\\]#).*$",mysLine)
# S E D   P R O P E R T I E S 
    elif ( re.match("^(properties|sed)$",mysType,re.I) ):
        TRC.trace(5,"proc match line as sed script")
        g.bShort =        0
        g.bCommentOnly = re.match("^\s*#.*$",mysLine)
        g.bCommentBegin = re.match("^\s*#.*$",mysLine)
        g.bCommentEnd = re.match("^\s*#.*$",mysLine)
        g.bCodeCommentBegin = 0
# I N I 
    elif ( re.match("^(ini)$",mysType,re.I) ):
        TRC.trace(5,"proc match line as INI file")
        g.bShort =        0
        g.bCommentOnly = re.match("^\s*[#;].*$",mysLine)
        g.bCommentBegin = re.match("^\s*[#;].*$",mysLine)
        g.bCommentEnd = re.match("^\s*[#;].*$",mysLine)
        g.bCodeCommentBegin = 0
# A N Y T H I N G   E L S E 
    else:
        TRC.trace(5,"proc match line as other random stuff")
        g.bShort = 0
        pass

# P H A S E   2 :   C L A S S I F Y   A N D   C O U N T   L I N E S 
    # Now count the various types of lines. 
    g.incLines()

    if ( g.bBlank ):
        g.incBlank()
    
    if ( g.bShort ): 
        g.incShort()
    
    if ( g.bCommentEnd ):
        bInCommentRegion = 0    
    
# P Y T H O N 
    if ( re.match("^(py)$",mysType,re.I) ):
        # All the reasonable logic here has been moved to the 
        # fnnEvalPythonCommentBlocksNEW routine.  
        # For no particularly good reason: it's no clearer there than here.
        fnnEvalPythonCommentBlocksNEW()

# N O T   P Y T H O N 
    else:
        if ( g.bCommentOnly ):
            # Comment line, not code line.
            g.incComment()
        elif ( g.bCommentBegin ):
            g.bInCommentRegion = 0
            if ( not g.bCommentEnd ):
                # Start of comment region, fersherr.  
                g.bInCommentRegion = 1
            if ( not g.bCodeCommentBegin ): 
                # If code on line, then don't count this line as comment.
                g.incComment()
        elif ( (not g.bCommentBegin) and g.bCommentEnd ):
            # End of comment region.
            g.bInCommentRegion = 0
            g.incComment()
        else:
            # Vanilla line.
            # If inside comment region, then comment, else code.
            if ( g.bInCommentRegion ):
                g.incComment()

    TRC.trace(3,"proc ProcessLine2 lines|%s| code|%s| blank|%s| short|%s| comment|%s|" % (g.getAll()))
    return 

# E X P E R I M E N T A L 
@tracef("EVPY")
def fnnEvalPythonCommentBlocksNEW():
    # Special convoluted counting for Python comment blocks
    # that begin and end with the same !@#$%&* sequenceS, grumble.
    ''' improved state machine:
    
    States for Python counting:
     - in code
        if #comment count comment line
        if blank count blank line
        count short line?
        if triple-apost count comment, begin triple-apost-region
        if triple-quote count comment, begin triple-quote-region
        else count code line
    - in triple-apostrophe
        count any line
        end triple-apost: leave region
    - in triple-doublequote
        count any line
        end triple-double: leave region
 
    '''   
    if g.bInCommentRegionApost:
        g.incComment()
        if g.bCommentBlockAloneApost or g.bCommentBlockTextBeforeApost:
            g.bInCommentRegionApost = False
    elif g.bInCommentRegionQuote:
        g.incComment()
        if g.bCommentBlockAloneQuote or g.bCommentBlockTextBeforeQuote:
            g.bInCommentRegionQuote = False
    else:
        if g.bCommentOnly:
            g.incComment()
        elif g.bShort:
            g.incShort()
        elif g.bCommentBlockSingleApost or g.bCommentBlockSingleQuote:
            g.incComment()
        elif g.bCommentBlockAloneApost or g.bCommentBlockTextAfterApost:
            g.bInCommentRegionApost = True
            g.incComment()
        elif g.bCommentBlockAloneQuote or g.bCommentBlockTextAfterQuote:
            g.bInCommentRegionQuote = True
            g.incComment()
        else:
            g.incCode()
    return ("Lines Code Comment InApost InQuote",g.nLines,g.nCode,g.nComment,g.bInCommentRegionApost,g.bInCommentRegionQuote)
# E N D  E X P E R I M E N T A L 


class G(object):
    ''' Class to contain all the global data.
        In the original Perl version, data names were more or less global
        all the time, unless you did something specific to override them.  
        Python's scoping rules are different, and painful at times, like now.  
        Rather than having all the code in one straight line outside
        a function, I prefer to isolate the code, sorta, but then I
        have to deal with global data.  This means either a pile of
        "global" statements in the procedure(s) or a global class.
        Pick the second one.  
        Tried to keep the count data in the procedure as a closure, but
        you can't update it, oops.  If you write the data, it is 
        automatically local.  So much for closures.  
    '''
    # Counters for types of lines.
    nLines = 0
    nBlank = 0
    nShort = 0
    nComment = 0
    nCode = 0
    # Functions to count with.  
    def incLines(self):
        self.nLines += 1
    def incBlank(self):
        self.nBlank += 1
    def incShort(self):
        self.nShort += 1
    def incComment(self):
        self.nComment += 1
    def incCode(self):
        self.nCode += 1
    # Return counters, some or all.  
    def getAll(self):
        return (self.nLines,self.nCode,self.nBlank,self.nShort,self.nComment)
    def getLine(self):
        return self.nLines
    # Boolean flags used per line to analyze type of line.
    bShort = 0
    bBlank = 0
    bComment = 0
    bCommentOnly = 0        # Comment on this line.  
    bCommentBegin = 0       # Comment with maybe something in front of it.  
    bCommentEnd = 0         # Comment end delimiter with maybe later text.
    bCode = 0
    bCodeCommentBegin = 0   # Code before comment on this line
    bInCommentRegion = 0    # In block comment, non-Python
    # Python-specific flags.
    bInCommentRegionApost = 0    # Inside block, potentially multiline, comment.
    bInCommentRegionQuote = 0    # Inside block, potentially multiline, comment.
    bCommentBlockAlone = 0      # Introducer/terminator alone on line.
    bCommentBlockTextAfter = 0  # Introducer with text after it.
    bCommentBlockTextBefore = 0 # Introducer after text.
    bCommentBlockTextBoth = 0   # Introducer with text on both sides.
    bCommentBlockSingle = 0     # Two introducers, probably begin-end, on line.

@trace
def fnProcessFile(mysFilename,mysFiletype):
    with open(mysFilename, "r") as fhInput:
        lLines = fhInput.readlines()
        for sLine in lLines:
            fnProcessLine(sLine,mysFiletype)

# Reduce match objects or None to one and zero, for brevity.  
def tf(something):
    if something:
        return 1
    else:
        return 0


if __name__ == "__main__":
    if len(argv) <= 1:
        print "Usage: python %s  input-filespec"
        print "       Line out = filename, filetype, total, code, comment, blank, short"
        print "       Output one line to stdout."
        exit(0)

    sFilename = argv[1]
    mFileext = re.match("^.*\.([^\.]+)$",sFilename,re.I)
    sFileext = mFileext.group(1)
    TRC.tracef(3,"MAIN","proc fname|%s| match|%s| ext|%s|" % (sFilename,mFileext,sFileext))

    g = G()                             # Instantiate all the global data.
    
    fnProcessFile(sFilename,sFileext)   # Do all this crap to the file.
    TRC.trace(3,"proc afterfile lines|%s| code|%s| blank|%s| short|%s| comment|%s|" % (g.getAll()))

    # The conservative way to calculate code lines is to remove 
    # everything that we saw that absolutely is not a line of code.
    # Blanks and comment-only lines are not code for sure.  
    # Short lines are arguable, so we report them separately.  
    (total,zerocode,blank,short,comment) = g.getAll()
    g.nCode = total - blank - short - comment   # Code is what's left over.
    # Finally, the single line of output for this file.  
    print "%s\t%s\t%d\t%d\t%d\t%d\t%d" % \
    (sFilename,sFileext,total,g.nCode,comment,blank,short)

# END
