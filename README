# Code Line Counter 
### A small Python program to count lines in program and documentation files

... and distinguish code lines from comment lines, blank lines, and short lines
in a large variety of computer languages.  Perhaps useful in looking at 
the size of software projects.  In particular, the density of comments 
in program source files may relate to the maintainability of the code.


## The Program

To invoke:

```
    python NewCodeLineCount.py <filespec>
```

Returns a single line of stats to stdout containing the following fields, 
tab-separated.  The output may be redirected ot teed to an output file.  

- filespec: the spec given to the program.

- file processed as: the language group of the file, which determines how 
the program searches for comment lines.  The program determines language 
group by looking at the file extension.  E.g., files of types ```.c, .cpp, 
.h, .hpp, .js, .java, .scala``` will all be processed as type
"```cpp/js/java```".  Files of unknown type will be processed as "```text```".

- total lines: count of all lines in the file.

- code lines: count of code lines in the file.  Code lines are calculated
simply as any line that is not identified as a comment, blank, or short.  

- comment lines: count of lines classified as comments, either single-line 
comments or block comments, relative to the programming language.

- blank lines: white space or empty.

- short lines: for languages that might have them, e.g., isolated braces 
in C, C++, Java, PHP, et al. 

Example output: (one line of output per program invocation; fields are
tab-separated)
```
    ./NewCodeLineCounts.py	python	475	285	102	88	0
    ./WeeklyCodeLineCounts_dir-08.sh	sh/perl/r	85	31	46	8	0
    ./CodeSupportedLanguages.txt	text	1	1	0	0	0
```

## The Script

There is a shell script to run line counting over entire directory trees.

To invoke: 

```
    sh WeeklyCodeLineCounts_dir.sh <directory>
```

The script processes all files of certain types in the directory tree.  The 
file types may be specified in a file, ```CodeSupportedLanguages.txt```, 
containing a single line of file types (extenstions), separated by blanks.  
Example:
```
    py pl sh ini txt r csv ins ins3 tpl j2 html c cpp h hpp java
```
The files will be processed in that order, one type at a time, down the
entire tree.  If no ```CodeSupportedLanguages.txt``` file is present in the 
current directory, then a default list of types will be used that contains 
the types of most common programming, resource, and documentation languages.

The script prints one header line to identify the several numeric fields, 
for the benefit of R, Excel, and such.  The header is also tab-separated.
Example header:
```
    file	type	total	code	comment	blank	short
```

All output goes to stdout.  The user may redirect or tee the output to 
be recorded in a file.

Happy counting.  

PS: The file ```NewTraceFac.py``` used by this program is a very old, 
traditional tracing facility.  It is turned off by default.  It can be 
turned on with environment variables; see the documentation in the 
source file, should you wish to use it.  


