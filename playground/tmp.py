image_dict = {
    'a': [1, 3, 4, 5],
    'b': [0, 2, 5, 6]
}

image_set = set()
for values in image_dict.values():
    for value in values:
        image_set.add(value)
print(image_set)
