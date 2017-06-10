#!/usr/bin/python
# t.py
# test program for Python line counter.

print("Hello, World!")
print("Hello again.")       # Code line with comment, too.
print('''Hello again again.''')
print("""Looks like a block comment but isn't.""")
''' begin block comment with single quotes
    inside block comment
'''
""" begin block comment with double quotes
    inside second block comment
"""

"""
# Nested comment, used to comment out a region of code that happened 
#  to contain a block comment.  
# Oops on this case, which is mis-handled currently.  To be fixed someday, 
#  maybe possibly perhaps, but a rare case that I won't lose much sleep over.  
print("This begins a code region that is commented out.")

'''
Block comment inside the a code region that now happens to be in a comment.
'''
print("Here endeth a code region that is commented out.")
print("This should count as comment, since it is commented out, but...")
print(" it probably counts as code.  Ask yourself, 'Do I care?'")
"""

if 0: '''
print("Code commented out the funny way.")
'''

#END
