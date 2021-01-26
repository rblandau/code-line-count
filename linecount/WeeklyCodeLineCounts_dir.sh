#!/bin/sh
#       WeeklyCodeLineCounts_dir.sh
#
#                   RBL 20030321
# Record the sizes of the source code files in a tree.  
# Scan all the files of all supported types in the given directory tree. 
#
# Supported file types taken from the file CodeSupportedLanguages.txt, if 
#  that file is present; otherwise, there is a default list that includes
#  just about everything plausibly a modern programming language.  
# 
# There is a default choice for the (Python) line-counter program, 
#  but this may be overridden by an environment variable 
#  LINECOUNTERPROGRAM naming another (still Python) program. 
# 

if [ -z "$1" ] 
then 
    echo "Usage: $0 source-tree-rootdir" 
    echo "Output, tab-sep, to stdout; redirect or tee to save to file."
    echo "e.g., $0 working/shelf | tee WeeklyCodeLineCounts_20170528.txt"
    echo "(All sh, pl, py, txt files to run this counter "
    echo " must be in the same directory as this shell script.)"
    exit 1 
fi

# Verify first arg is a directory suitable for find
if [ ! -d "$1" ] ; then echo "Error: $1 must be a directory" ; exit 2 ; fi

# Get list of languages from canned list, if present; else use standard list.
sSupportedLanguageFile="`dirname $0`/CodeSupportedLanguages.txt"
if [ -r "$sSupportedLanguageFile" ] 
then
    sSupportedLanguages=`cat $sSupportedLanguageFile`
else
    sSupportedLanguages="py py2 py3 pm js gs r c cpp h hpp java xml xsl html xhtml xml xsl tpl j2 bat cmd sh csv mak pl awk sed ini txt md rst"
fi

# Use latest version of default program, unless the user has specified
#  an alternate program.
if [ -z "$LINECOUNTERPROGRAM" ]
then
    # Find the highest numbered version of the counter program.  
    latestprogram=$(ls NewCodeLineCounts*.py | sort | tail -1 | sed 's/\\r//')
    LINECOUNTERPROGRAM=$latestprogram
fi

# Start with header line for Excel or R to recognize.
# Tab-separated.
#echo "FILE\tTOTAL\tCODE\tCOMMENT\tBLANK\tSHORT" 
echo "file	type	total	code	comment	blank	short" 
for sSrcType in $sSupportedLanguages
do 
    find "$1" -name "*.$sSrcType" -print | while read sFilename 
            do
                #echo python `dirname $0`/$latestprogram "${sFilename}"
                python `dirname $0`/$LINECOUNTERPROGRAM "${sFilename}"
            done
done 

# From dev/learn/bash/t1.sh, sorta:
#find "$1" -print | while read f; do echo $f; done

exit 0

# Edit history:
# 20030324  RBL Original version.  
# 20030523  RBL Add header line in output file.
# 20081013  RBL Error-proof second argument (output file).
#               Add ini as a file type.
# 20120711  RBL Add ini as file type.
#               Change to python counter program.
#               Avoid xargs.  
#               Remove second arg; user can redirect or tee.  
#               Change column names to lowercase.  
#               Always use latest version of counting program.  
# 20150102  RBL Improve usage and comments.  
#               Eliminate traces of output file arg.  
# 20170522  RBL Add types tpl and j2 for Jinja2 templates.
# 20170530  RBL Allow env var LINECOUNTERPROGRAM to override
#                default counter program, to make it easy to
#                test old against new for regression.  
# 
# 
#END
