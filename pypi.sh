#!/bin/bash

# Ensure pip install twine wheel

if [[ "x$1" == "xbuild" ]] ; then
    python3 setup.py sdist bdist_wheel

elif [[ "x$1" == "xtestpush" ]] ; then
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*

elif [[ "x$1" == "xpush" ]] ; then
    echo "Will push to REAL PyPI!!! Sleeping 60 secs"
    sleep 60
    twine upload dist/*

elif [[ "x$1" == "xclean" ]] ; then
    # Remove build artifacts
    rm -rf build dist propertime.egg-info

else
    echo "Usage: pypi.sh [build|testpush|push|clean]"

fi


