import inspect

def printFunc(foo):
    lines = inspect.getsource(foo)
    print(lines)

def printListWithArrow(list, N):
    print(list)
    print(" "*(3*N+1) + "^")

def iterateThroughList(list, N):
    for i in range(N):
        printListWithArrow(list, i)

def nextFibonacci(A, n):
    if n == 0 or n == 1:
        return 1
    return A[n-1] + A[n-2]

def fibonacci(N):
    A = [0]*N
    print(A)
    for i in range(N):
        A[i] = nextFibonacci(A, i)
        printListWithArrow(A, i)
    return A 

N = 5
A = [0]*N

A = fibonacci(N)
