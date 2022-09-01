#!/bin/bash

py -m build --wheel

py -m twine upload --repository pypi dist/*.whl