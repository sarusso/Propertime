#!/bin/bash

# Tested with:
# pip install twine==4.0.2 wheel==0.42.0
#Ensure pip install twine wheel

if [[ "x$1" == "xbuild" ]] ; then
    python3 setup.py sdist bdist_wheel

elif [[ "x$1" == "xtestpush" ]] ; then
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*

elif [[ "x$1" == "xpush" ]] ; then
    echo ""
    echo " !!! Will push to REAL PyPI !!! "
    echo ""
    sleep 3
    twine upload dist/*

elif [[ "x$1" == "xclean" ]] ; then
    # Remove build artifacts
    rm -rf build dist propertime.egg-info

else
    echo "Usage: pypi.sh [build|testpush|push|clean]"

fi


