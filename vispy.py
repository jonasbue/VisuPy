import inspect

def printListWithArrow(content, N):
    print(content)
    print(" "*(3*N) + "^")


A = [1,2,3,4,5,6,7]
N = 3

printListWithArrow(A, N)

def printFunc(foo):
    lines = inspect.getsource(foo)
    print(lines)

printFunc(printListWithArrow)
