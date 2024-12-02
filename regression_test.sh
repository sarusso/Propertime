#!/bin/bash
set -e

for PYTHON_VERSION in "3.6" "3.7" "3.8" "3.9" "3.10" "3.11" "3.12" "3.13"; do

    echo ""
    echo "=========================="
    echo " Testing with Python $PYTHON_VERSION "
    echo "=========================="

    docker run -it -v $PWD:/Propertime python:$PYTHON_VERSION /bin/bash -c "cd /Propertime && pip install -r requirements.txt && python -m unittest discover"
done
