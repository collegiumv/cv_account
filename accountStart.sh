#!/bin/sh
mkdir -p log
touch ./log/accountService.log

tmux new-session -s accountService -d 'python main.py'
sleep 5
tmux new-window -t accountService:1 -n 'Account Log' 'tail -f ./log/accountService.log'
