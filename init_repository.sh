#!/bin/bash

set -e

echo -n Setting up Git pre-commit hook...

cp ./assets/pre-commit ./.git/hooks/pre-commit

echo Done.

echo -n Setting up virtual environment...

python3 -m venv venv

echo Done.

echo Install requirements locally...

source ./venv/bin/activate
pip install -r requirements.txt

echo Done.
