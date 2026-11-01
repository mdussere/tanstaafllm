#!/bin/sh
# Mike's header (Wyoh 6.13, look A), printed in Mike's foot window before its
# client starts: the portrait (sixel, from the series' key art), the name, the
# keys. Colours are the foot-mike.ini palette (33 amber, 36 cyan, 34 violet).
here=$(dirname "$(readlink -f "$0")")
cat "$here/mike-portrait.six"
printf '\n\033[1;33mMIKE\033[0m  \033[90mLuna\047s local brain\033[0m\n'
printf '\033[36mL2 dictate · FN+B send · /new forget · /quit\033[0m\n'
printf '\033[34m────────────────────────────────────────\033[0m\n\n'
