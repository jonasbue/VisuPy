import visupy

def hardFunc():
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


def basicFunc():
    x = 2
    if x == 2:
        print(x)
    else:
        x = 2

def fib(n):
    l = []
    for i in range(n):
        if len(l) == 0 or len(l) == 1:
            l.append(1)
        else:
            l.append(l[i-1]+ l[i-2])
            print('hello')
        print(x)
        print(x)
        print(x)
        print(x)
        print(x)
        print(x)
    print(l)

def test1():
    x = 1

    y = 0
    if x==1:
        print("hei")
        x = 4
    else:
        print("ha det bra")
        t = 3
        z = 1
    for i in range(3):
        y += x
        y = 2**y
        r = 1
        z = x + y
    if 3==4:
        x,y = y,x
    else:
        x += 1
        y -= 2 

visupy.visualize(basicFunc, 'basic')
visupy.visualize(fib, 'fib')
visupy.visualize(hardFunc, 'hard')
visupy.visualize(test1, 'test1')

