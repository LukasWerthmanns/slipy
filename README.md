# slipy
Terminal based file manager that uses vim-like bindings

## Programs
Slipy uses mpv, sxiv and zathura to open files. There is currently no support for other programs

## Commands
# Movement
h	- Move down in filepath

j	- Move down one entry

k	- Move up one entry

l	- Open file (see list of used programs)

g	- Jump to first entry

G	- Jump to last entry

L	- Jump to last entry that is currently on screen

H	- Jump to first entry that is currently on screen

# Utility
t	- Touch file (prompts for name)

m	- mkdir (prompts for name)

d	- Delete current entry

r	- Rename current entry

R	- Refresh directory contents

# Marking
v	- mark entry

V	- toggle mark mode

	  use j and k to go up and down to mark elements

M	- Move all marked elements into current Directory

D	- Delete all marked Elements

# Prompt
:	- Open command prompt

:mkdir / :m 		- same as "m" command

:touch / :t		- same as "t" command

:delete marked / ":DM 	- same as "D" command

:move marked   / ":MM	- same as "M" command

:q			- quit
