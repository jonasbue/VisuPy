import inspect
import string
import subprocess, os
from sys import platform


class CodeLine:
    def __init__(self, id, type, contents, parent):
        """Creates a new CodeLine object.
        id is the line number in the function.
        type can be: start, io, if, for, while, misc
        contents is the string with the code for this line
        """

        self.id = int(id)  # Line number
        self.type = type.lower()
        self.contents = str(contents.strip())
        self.parent = parent if parent != -1 else self  # Parent box. Set to self if no parent (i.e. start)

        self.makeChild()

        self.children = []  # List of children boxes
        self.num_children = 0

        self.orientation = "below"  # Can be changed to move relative position to parent box
        self.offset = (0, 0)  # (x, y) offset from parent box. If (0, 0) use Latex default

    def makeChild(self):
        if self.parent != self:
            self.parent.children.append(self)
            self.parent.num_children += 1

    def drawBox(self):
        print(self.contents)
        if self.type == "if":
            boxstyle = "decision"
        elif self.type == "for":
            boxstyle = "process"
        elif self.type == "io":
            boxstyle = "io"
        elif self.type == "while":
            boxstyle = "process"
        elif self.type == "start":
            boxstyle = "startstop"
            return '\\node (box0) [startstop] {' + str(self.contents).rstrip() + '};\n'
        else:
            boxstyle = "process"

        if self.parent != self:
            pos = "{orientation} of= box{parent}".format(orientation=self.orientation, parent=self.parent.id)
            if self.offset[0] != 0:
                pos += ", xshift={shift}cm".format(shift=self.offset[0])
            if self.offset[1] != 0:
                pos += ", yshift={shift}cm".format(shift=self.offset[1])
        else:
            pos = ""

        return '\\node (box{id}) [ {type} , {pos}]{code};\n'.format(id=self.id,
                                                                     type=boxstyle,
                                                                     pos=pos,
                                                                     code="{" + self.contents + "}")

    def drawArrows(self):
        arrows = ""
        for child in self.children:
            # If the child is older than the parent (ie. feedback),
            # then the arrow takes a round shape.
            if self.id > child.id:
                arrows += '\draw [arrow] (box{id}) to [bend left] (box{child});\n'.format(id=self.id, child=child.id)
            else:
                arrows += '\draw [arrow] (box{id}) -- (box{child});\n'.format(id=self.id, child=child.id)
        return arrows


def findIndentation(line):
    return len(line) - len(line.strip())


# Finds the number of lines in a loop, excluding the declaration line
def findEndOfLoop(function, startLine, stopAtKeyword=False):
    a = startLine + 1
    lastLineNumber = len(inspect.getsourcelines(function)[0])
    numberOfLinesInLoop = 1

    line = inspect.getsourcelines(function)[0][startLine]
    indentation = len(line) - len(line.lstrip())

    # Number of leading spaces in the for loop declaration
    line = inspect.getsourcelines(function)[0][a]

    while len(line) - len(line.lstrip()) > indentation and a < lastLineNumber:
        line = inspect.getsourcelines(function)[0][a]
        if stopAtKeyword == True:
            if line.find('if') != -1 or line.find('for') != -1:
                break
        numberOfLinesInLoop += 1
        a += 1
    return numberOfLinesInLoop


def convertLeadingSpaces(line, ignored):
    n = (findIndentation(line) - ignored) // 4
    line = line.lstrip()
    for i in range(n):
        line = "\\hspace{8pt} " + line
    print(line)
    return line


def write_latex(code):
    with open('sometexfile.tex', 'w') as f:
        f.write('\\documentclass{article}\n')
        f.write('\\usepackage{tikz}\n \\usetikzlibrary{shapes.geometric, arrows,arrows.meta, positioning, fit}\n')

        # tikz styles
        f.write(
            '\\tikzstyle{startstop} = [rectangle, rounded corners, minimum width=3cm, minimum height=1cm,text centered, draw=black, fill=red!30]\n')
        f.write(
            '\\tikzstyle{io} = [trapezium, trapezium left angle=70, trapezium right angle=110, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=blue!30]\n')
        f.write(
            '\\tikzstyle{process} = [rectangle, minimum width=3cm, minimum height=1cm, text width=3cm, text centered, draw=black, fill=orange!30]\n')
        f.write(
            '\\tikzstyle{decision} = [ellipse, minimum width=3cm, minimum height=1cm, text width=3cm, text centered, draw=black, fill=green!30]\n')
        f.write('\\tikzstyle{arrow} = [thick,->,>=stealth]\n')
        f.write('\\title{Visualize!} \date{}\n')
        f.write('\\begin{document}\n')
        f.write('\maketitle\n')

        # Start  your flowchart
        f.write('\\begin{tikzpicture}[node distance = 2cm]\n')
        f.write(code)

        f.write('\\end{tikzpicture}\n')
        f.write('\\end{document}\n')


def test():
    x = 1
    y = 0
    for i in range(3):
        y += x
        y = 2**y
        x *= y
    z = x + y

def findBoxType(line):
    if line.count("=") == 1:
        type = "io"
    elif line.find("for") != -1:
        type = "for"
    elif line.find("while") != -1:
        type = "while"
    elif line.find("if") != -1:
        type = "if"
    elif line.find("else") != -1:
        type = "if"
    else:
        type = "misc"
    return type

boxes = []
raw_code = inspect.getsourcelines(test)[0]

for i, line in enumerate(raw_code):
    if i == 0:
        parent = -1
        type = "start"
    else:
        parent = boxes[i - 1]   # This gives every box a unique parent
                                # For lines related to if/else,
                                # some logic is needed
        type = findBoxType(line)

    boxes.append(CodeLine(i, type, line, parent))
    boxes[i].offset = (0, 0)

def drawFeedback(CodeLine):
    start = boxes[CodeLine.id]
    end = findEndOfLoop(test, CodeLine.id) + CodeLine.id - 2
    boxes[end].children = []
    boxes[end].children.append(start)
    boxes[end].num_children += 1

def drawExit(CodeLine):
    end = findEndOfLoop(test, CodeLine.id) + CodeLine.id - 1
    boxes[end].offset = (-5,0)
    CodeLine.children.append(boxes[end])
    CodeLine.num_children += 1

for i in range(len(boxes)):
    if boxes[i].type == "for" or boxes[i].type == "while":
        boxes[i+1].offset = (5,2)
        drawFeedback(boxes[i])
        drawExit(boxes[i])



string = ""

for box in boxes:
    string += box.drawBox()

for box in boxes:
    string += box.drawArrows()

write_latex(string)

x = os.system("pdflatex ./sometexfile.tex")
if x != 0:
    print('Exit-code not 0, check result!')
else:
    if platform == "linux" or platform == "linux2":
        os.system('xdg-open sometexfile.pdf')

    elif platform == "darwin":
        os.system('open sometexfile.tex')
        os.system('open sometexfile.pdf')

    elif platform == 'win32':
        os.system('start sometexfile.pdf')

def fib(n):
    l = []
    m = [1,2,3]
    for i in range(n):
        if len(l) == 0 or len(l) == 1:
            el = [0]
        else:
            el = l[i-1]+l[i-2]

        l.append(el)
    print(l)






def vis(myFun):
    # open a new/clear tex
    with open('sometexfile.tex','w') as f:
        f.write('\\documentclass{article}\n')
        f.write('\\usepackage{tikz}\n \\usetikzlibrary{shapes.geometric, arrows,arrows.meta, positioning, fit}\n')

        # tikz styles
        f.write('\\tikzstyle{startstop} = [rectangle, rounded corners, minimum width=3cm, minimum height=1cm,text centered, draw=black, fill=red!30]\n')
        f.write('\\tikzstyle{io} = [trapezium, trapezium left angle=70, trapezium right angle=110, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=blue!30]\n')
        f.write('\\tikzstyle{process} = [rectangle, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=orange!30]\n')
        f.write('\\tikzstyle{decision} = [ellipse, minimum width=3cm, minimum height=1cm, text width=3cm, text centered, draw=black, fill=green!30]\n')
        f.write('\\tikzstyle{arrow} = [thick,->,>=stealth]\n')
        f.write('\\title{Visualize!} \date{}\n')
        f.write('\\begin{document}\n')
        f.write('\maketitle\n')

        # Start  your flowchart
        f.write('\\begin{tikzpicture}[node distance = 2cm]\n')
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
        ifC = 0
        i = 1 

        numberOfLines = len(inspect.getsourcelines(myFun)[0])

        # Go line by line through the function
        i = 1
        while i < numberOfLines:
            line = inspect.getsourcelines(myFun)[0][i]

            # If this is an initialization line
            if line.count('=') == 1:

                # new box
                newBox = 'in' + str(ioC)

                # str = make node + call what is in line
                s = '\\node (' + newBox + ') [io, below of=' + prevBox +'] {' + line + '};\n'
                f.write(s)

                #\draw arrow from last box to new box
                f.write('\draw [arrow] ('+prevBox+') -- ('+newBox+');\n')
                #update prevBox
                prevBox = newBox

                # increase number of io boxes
                ioC += 1

            # If a for loop is found
            if line.find('for') != -1:

                newBox = 'for' + str(frC)

                loopLength = findEndOfLoop(myFun, i, stopAtKeyword=True)
                loopIndentation = findIndentation(line)
                loopLines = ''

                s = '\\node (' + newBox + ') [process, below of=' + prevBox +'] {'
                for j in range(loopLength):
                    s += "\n" + convertLeadingSpaces(inspect.getsourcelines(myFun)[0][i+j], loopIndentation)

                s += '};\n'

                f.write(s)

                # Storing the for loop box so that later nodes can loop back
                prevFor = newBox

                frC += 1

                # This line makes the searcher skip lines within the for loop,
                # but I thought it was more difficult to read the resulting chart,
                # so I commented it out:
                #i += loopLength - 1

                #\draw arrow from last box to new box
                f.write('\draw [arrow] ('+prevBox+') -- ('+newBox+');\n')
                #update prevBox
                prevBox = newBox



            if line.find('if') != -1:
                newBox = 'if' + str(ifC)

                s = '\\node (' + newBox + ') [decision, below of=' + prevBox + '] {' + line + '};\n'

                # if True:
                 
                newBoxT = newBox + 'T'
                sT = '\\node ('+ newBoxT + ') [process, below right=of ' + newBox + ']{'+ inspect.getsourcelines(myFun)[0][i+1]+'};\n'
               
                s = s + sT 
                f.write(s)
                  

                # now join back to the previous for loop

                f.write('\draw [arrow] ('+ newBoxT + ') to [bend right] (' + prevFor + ');\n')
                f.write('\draw [arrow] ('+newBox+') -- node {True}('+newBoxT+');\n')
               
                # We now know that we can skip these lines as they are dealt with 
                # i+1 is the content of the if statement
                i+=2
                ifC += 1

                #\draw arrow from last box to new box
                f.write('\draw [arrow] ('+prevBox+') to ('+newBox+');\n')


                #Need to check if there are following elif statements
                linearr = inspect.getsourcelines(myFun)[0]
                print(linearr[i])
                if linearr[i].find('elif') != -1 or linearr[i].find('else') != -1:
                    # we have an else statement
                    
                    # if False
                    newBoxF = newBox + 'F'
                    sF = '\\node ('+ newBoxF + ') [process, below left=of ' + newBox + ']{'+ inspect.getsourcelines(myFun)[0][i+1]+'};\n'
                    f.write(sF)
                    f.write('\draw [arrow] ('+newBox+') -- node {elif}('+newBoxF+');\n')
                    
                    # now we need to skip past all of the elif stuff
                    i += 1
                    
                    # loop back to the prevoius for loop
                    f.write('\draw [arrow] (' + newBoxF + ') to [bend left] (' + prevFor + ');\n') 

            #update prevBox
            prevBox = newBox

            i += 1
            

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
        if platform == "linux" or platform == "linux2":
            os.system('xdg-open sometexfile.pdf')
            #os.system('xdg-open sometexfile.tex')

        elif platform == "darwin":

            os.system('open sometexfile.tex')
            os.system('open sometexfile.pdf')
        elif platfom == 'win32':
            pass


    '''
    for line in inspect.getsourcelines(myFun)[0][0]:
        # returns -1 if there is no = sign
        if line.count('=') == 1:
            obj = eval(line.split("=", 1)[1])
            #fstwrd = line.split()[0]
            print(obj)
            print(type(obj))
'''
#vis(fib)
