#!/bin/sh
set -e
cd "$(git rev-parse --show-toplevel)"
mypy $(find ./python/ -maxdepth 3 -name '__init__.py' -printf '%h\n')
