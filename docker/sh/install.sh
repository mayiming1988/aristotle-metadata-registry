#!/usr/bin/env bash
# pipenv lock
# pipenv graph
# pipenv install --dev --system
cd ..
pipenv install --dev --system --skip-lock
cd docker
