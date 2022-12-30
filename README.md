# cross-ref-py:  Side to Side Cross Reference

Visualization of 2 files side to side where
one of them is a generated version of the other. Line number
correspondence is provided in a separate file.

# Introduction

This utility displays two files side to side. When one line in
one of them is clicked it gets highlighted along with the 
corresponding(s) on the other side.

# Cross Reference File

This is an example of a cross reference file:

    1:1
    2:2
    3:3-
    4-10:7-20
    11-:21-

* left of the ":" represent line numbers on left file
* right of the ":" represent corresponding line numbers on right file
* each line represents a group, where lines on the left maps to the ones on right and vice-versa
* lines number on each side are represented by a comman separated list of numbers or ranges of
  numbers. If a range is open on the right (e.g. 3-) the right side limit is the line before the 
  minimum line of the next group

    in the example above 3:3- maps line 3 (left) to the range 3-6 (right)


Note that if you have a file including 'line' directives it is straightforward to convert to
this format (this format being more general)

For example a right file with #line's embedded as follows:

    /---- Line number of right file
    |
    v
    1: #line 1   <-- reference to line on left file
    2:
    3: #line 2
    4:
    5:
    6: #line 5

Would correspond to:

    1-:1-
    2-:3-
    5-:6-

