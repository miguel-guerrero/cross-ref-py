# Side to Side Cross Reference Visualization

Visualization of 2 files side to side where
one of them is a generated version of the other. Line number
correspondence is provided in a separate cross reference file.

This utility is useful to visualize original source code when navigating 
a code listing generated from it, tipycally a less readable lower level 
representation. Allows you to:

- Visualize corresponding source code when pointing to a specific piece of the
generated code.

- Visualize corresponding low level code that has been generated from a portion
of high level code.

# Introduction

This utility displays two files side to side. When one line in
one of them is clicked it gets highlighted along with the 
corresponding(s) on the other side.

# Cross Reference File

This is an example of a cross reference file:

    1:1
    2:2
    3:3-
    4-10:7, 9-20
    11-:8,21-

* Left of the ":" represent line numbers on left file.
* Right of the ":" represent corresponding line numbers on right file.
* Each line represents a group, where lines on the left map to the lines on right and vice-versa.
* Lines numbers on each side are represented by a comma separated list of ranges of
  numbers. If a range is open on the right (e.g. 3-) the right side limit is the line before the 
  minimum line of the next group. A range can be a single line number as well (no -).

    in the example above 3:3- maps line 3 (left) to the range 3-6 (right) as 7 is the beginning line
    of the next group on the right.


Note that if you have a file including `line` directives (see [preprocessor documentation](https://gcc.gnu.org/onlinedocs/cpp/Line-Control.html)), it is straightforward to convert to
this format (this format being more general).

For example a right file with `#line` directives embedded as follows:

    v---- Line number of right file
    
    1: #line 1   <-- reference to line on left file
    2:
    3: #line 2
    4:
    5:
    6: #line 5
    7:
    8:
    
Can be represented in this format with the following cross reference file:

    1-:2-
    2-:4-
    5-:7-

Where the line number `n` on the left comes from the `#line n` directive, and the one on the right is the line number where the `#line n` directive is located plus one.

## Usage

Invoking the script without dependencies shows a GUI. Load left and right files, then cross-reference file.

    ./cross-ref.py

you can also pass the path to these files in the command line:

* if no argument is given, a clean slate GUI opens up
* if 1 argument is given is assumed left file and will be loaded when the GUI opens up

    `./cross-ref.py pathToLeft`
    
* if 2 arguments are given they are assumed to be left and right file respectively and will be loaded when the GUI opens up

    `./cross-ref.py pathToLeft pathToRight`

* if 3 arguments are given they are assumed to be left, right and cross reference file respectively and will be loaded when the GUI opens up

    `./cross-ref.py pathToLeft pathToRight pathToCrossRef`

Clicking a line on one file will highlight the corresponding lines on the same group on the same side and on the other side.

## Dependencies

This script uses `python3` (version 3.10.9 at time of testing but any should be ok) and `tkinter`. It has been tested in MacOS. 
In MacOS `tkinter` was installed for the above version of `python3` as:

    brew install python-tk@3.10
    
A similar approach is expected for other versions.


