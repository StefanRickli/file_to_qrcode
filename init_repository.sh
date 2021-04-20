#!/bin/bash

set -e

echo Setting up Git pre-commit hook...

cp ./assets/pre-commit ./.git/hooks/pre-commit

echo Done.
