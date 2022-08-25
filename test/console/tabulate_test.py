import tabulate
data = [
    ['id', 'name', 'number'],
    [0, 'Jeff', 1234],
    [1, 'Bob', 5678],
    [2, 'Bill', 9123]
]
results = tabulate.tabulate(data)
print(results)

# --  ----  ------
# id  name  number
# 0   Jeff  1234
# 1   Bob   5678
# 2   Bill  9123
# --  ----  ------