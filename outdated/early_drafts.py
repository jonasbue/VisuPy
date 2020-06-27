import inspect

def printFunc(foo):
    lines = inspect.getsource(foo)
    print(lines)

def printListWithArrow(l, N):
    print(l)
    print(" "*(3*N+1) + "^")

def iterateThroughList(l, N):
    for i in range(N):
        printListWithArrow(l, i)

def nextFibonacci(A, n):
    if n == 0 or n == 1:
        return 1
    return A[n-1] + A[n-2]

def fibonacci(N):
    A = [0]*N
    #print(A)
    for i in range(N):
        A[i] = nextFibonacci(A, i)
        #printListWithArrow(A, i)
    return A 

def scanThroughFunc(foo):
    lines = inspect.getsourcelines(foo)
    for line in lines[0][:]:
        if line.find("=") != -1:
            print(line)
            exec(line.strip())
            
def visualizeObject(obj):
    if type(obj) is list:
        printList


N = 5
A = [0]*N

A = fibonacci(N)

#scanThroughFunc(fibonacci)


def fib(n):
    l = []
    for i in range(n):
        if len(l) == 0 or len(l) == 1:
            el = 1
    else:
        el = l[i-1]+l[i-2]
        l.append(el)
        print(l)

#fib(10)


def vis(myFun):
    for line in inspect.getsourcelines(myFun)[0][1:]:
        # returns -1 if there is no = sign
        if line.count('=') == 1:
            obj = eval(line.split("=", 1)[1])
            #fstwrd = line.split()[0]
            print(obj)
            print(type(obj))

vis(fibonacci)

