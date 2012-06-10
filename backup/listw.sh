#!/bin/bash
p4 workspaces | egrep tmackall | perl -ne 's/Client ([^ ]*).*/$1/' -p | egrep ^tmackall
