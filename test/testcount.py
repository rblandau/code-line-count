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

'''
block comment containing blank line

# and line that appears to be single-line comment
print("foo")    # and line that appears to be code+comment
# and line that appears to be just code
print("bar")
'''

if 0: '''
print("Block of code commented out the funny way.")
# Still have to be careful about triple quotes inside the block.
'''

#END
