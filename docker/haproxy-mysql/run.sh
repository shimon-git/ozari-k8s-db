#!/bin/bash
alias dc='docker compose'
dc down
dc -p haproxy up -d