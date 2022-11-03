import time

def fun1():
    time.sleep(1)

def fun2():
    time.sleep(1)

def fun3():
    time.sleep(2)

def fun4():
    time.sleep(1)

def fun5():
    time.sleep(1)
    fun4()

fun1()
fun2()
fun3()
fun5()