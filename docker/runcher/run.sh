#!/bin/bash
alias dc='docker compose'
dc down
dc -p runcher up -d