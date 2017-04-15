Description
===========

RM analogue

Config example:

JSON
{
  "trash": "/home/pride/Workspace/univ/python/lab2/trash/",
  "log_path": "/home/pride/Workspace/univ/python/lab2/mylog.log",
  "dry": false,
  "silent": false,
  "confirm": false,
  "policy": "size",
  "force": false
}

TXT
"trash": "/home/pride/Workspace/univ/python/lab2/trash/"
"log_path": "/home/pride/Workspace/univ/python/lab2/mylog.log"
"dry": 0
"silent": 0
"confirm": 0
"policy": "size",
"force": 0

@params:
    trash - path to trash
    log_path - path to log file
    dry - default dry mode value
    silent - default silent mode value
    confirm - default confirmation mode value
    force - default force mode value
    policy - policy keu word (size or time)
