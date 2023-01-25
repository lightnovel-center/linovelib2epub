# 在本地开发环境中发布

## PYPI
```bash
#py -m build
py -m build --wheel
py -m twine upload --repository pypi dist/*.whl
```

## TESTPYPI
```bash
py -m build --wheel
py -m twine upload --repository testpypi dist/*.whl
```