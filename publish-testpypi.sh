#!/bin/bash

py -m build --wheel
# get the name of generated whl file

# replace *.whl with the name of previous whl
py -m twine upload --repository testpypi dist/*.whl