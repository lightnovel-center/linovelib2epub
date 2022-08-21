class Fruits: pass


banana = Fruits()

banana.color = 'yellow'
banana.value = 30

import pickle

filehandler = open("Fruits.obj", "wb")
pickle.dump(banana, filehandler)
filehandler.close()

file = open("Fruits.obj", 'rb')
object_file = pickle.load(file)
file.close()

print(object_file.color, object_file.value, sep=', ')
# yellow, 30
