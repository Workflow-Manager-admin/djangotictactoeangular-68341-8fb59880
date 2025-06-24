#!/bin/bash
cd /home/kavia/workspace/code-generation/djangotictactoeangular-68341-8fb59880/game_backend_workspace/game_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

