import visupy

# The following are test functions that demonstrate how VisuPy works.

def basicFunction():
    x = 2
    if x == 2:
        print(x)
    else:
        x += 2
    return x


def fibonacci(n):
    L = []
    for i in range(n):
        if len(L) == 0 or len(L) == 1:
            L.append(1)
        else:
            a = L[i-1]
            b = L[i-2]
            L.append(a - b)
    return L


def hardFunction():
    x = 1
    if x == 1:
        y = 4
        z = x + y
    else:
        y = 0
        z = 0
    z = z ** 2
    if y == 2:
        print('y is 2')
    print('The end')
    for i in range(2):
        print("hi")
        x = 4
    x = 3

    if z == 3:
        print("oh no")
        print("1")
    else:
        print("oops")

    print('end')

visupy.visualize(basicFunction, 'basic')
visupy.visualize(fibonacci, 'fibonacci')
visupy.visualize(hardFunction, 'hard')
