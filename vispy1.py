import inspect
import string
import subprocess, os


def printListWithArrow(content, N):
    print(content)
    print(" "*(3*N) + "^")

def printFunc(foo):
    lines = inspect.getsource(foo)
    print(lines)

def printListWithArrow(list, N):
    print(list)
    print(" "*(3*N+1) + "^")

def iterateThroughList(list, N):
    for i in range(N):
        printListWithArrow(list, i)
'''
#printListWithArrow(A, N)
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

#print(inspect.getsource(printFunc))

'''


def fib(n):
    l = []
    m = [1,2,3]
    for i in range(n):
        pass
'''
        if len(l) == 0 or len(l) == 1:
            el = 1
        else:
            el = l[i-1]+l[i-2]
        l.append(el)
    print(l)
'''
#fib(10)


def vis(myFun):
    # open a new/clear tex
    with open('sometexfile.tex','w') as f:
        f.write('\\documentclass{article}\n')
        f.write('\\usepackage{tikz}\n \\usetikzlibrary{shapes.geometric, arrows}\n')

        # tikz styles
        f.write('\\tikzstyle{startstop} = [rectangle, rounded corners, minimum width=3cm, minimum height=1cm,text centered, draw=black, fill=red!30]\n')
        f.write('\\tikzstyle{io} = [trapezium, trapezium left angle=70, trapezium right angle=110, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=blue!30]\n')
        f.write('\\tikzstyle{process} = [rectangle, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=orange!30]\n')
        f.write('\\tikzstyle{decision} = [diamond, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=green!30]\n')
        f.write('\\tikzstyle{arrow} = [thick,->,>=stealth]\n')
        f.write('\\title{Visualize!} \date{}\n')
        f.write('\\begin{document}\n')
        f.write('\maketitle\n')

        # Start  your flowchart
        f.write('\\begin{tikzpicture}[node distance=2cm]\n')
        funcName = inspect.getsourcelines(myFun)[0][0]
        #        print(funcName)
        
        # Start flow chart with name of function
        s = '\\node (start) [startstop] {' + str(funcName).rstrip() + '};\n'
        f.write(s)

        # Need to keep track of previous box
        prevBox = 'start'
        newBox = None
        # Need to keep track of how many io box to call correctly
        ioC = 0
        frC = 0

        # Go line by line
        for line in inspect.getsourcelines(myFun)[0][1:]:

            # If this is an initialization line
            if line.count('=') == 1:

                # new box
                newBox = 'in' + str(ioC)

                # str = make node + call what is in line
                s = '\\node (' + newBox + ') [io, below of=' + prevBox +'] {' + line + '};\n'
                f.write(s)
                


                # increase number of io boxes
                ioC += 1

            if line.find('for') != -1:

                newBox = 'for' + str(frC)

                s = '\\node (' + newBox + ') [process, below of=' + prevBox +'] {' + line + '};\n'
                f.write(s)


                frC += 1
                
            #\draw arrow from last box to new box
            f.write('\draw [arrow] ('+prevBox+') -- ('+newBox+');\n')
            #update prevBox
            prevBox = newBox


            '''
                obj = eval(line.split("=", 1)[1])
                #fstwrd = line.split()[0]
                print(obj)
                print(type(obj))
'''


        f.write('\\end{tikzpicture}\n')
        f.write('\\end{document}\n')
    

    # -interaction=batchmode
    x = os.system("pdflatex ./sometexfile.tex")
    if x != 0:
        print('Exit-code not 0, check result!')
    else:
        os.system('open sometexfile.tex')
        os.system('open sometexfile.pdf')


    '''
    for line in inspect.getsourcelines(myFun)[0][0]:

        # returns -1 if there is no = sign
        if line.count('=') == 1:
            obj = eval(line.split("=", 1)[1])
            #fstwrd = line.split()[0]
            print(obj)
            print(type(obj))
'''
vis(fib)


