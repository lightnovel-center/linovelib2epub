# python parse json

- 使用 json 库，要求对象的key必须为double quotes格式`{"x":1}`，不能为字面类型`{x:1}`以及单引号类型`{'x':1}`。
- 使用demjson
- 使用一段helper代码
```python
rs = eval(str_1, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
```