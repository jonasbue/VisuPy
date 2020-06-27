import inspect
import string
import subprocess, os
from sys import platform


class CodeLine:
    def __init__(self, id, contents, parent):
        """Creates a new CodeLine object.
        id is the line number in the function.
        type can be: start, io, if, else, for, while, misc
        contents is the string with the code for this line
        """

        self.id = int(id)               # Line number
        self.contents = str(contents.strip())
        self.type = self.getType()

        self.parent = parent if parent != -1 else self  # Parent box. Set to self if no parent (i.e. start)
        self.makeChild()

        self.children = []              # List of children boxes
        self.num_children = 0

        self.orientation = "below"      # Can be changed to move relative position to parent box
        self.offset = (0, 0)            # (x, y) offset from parent box. If (0, 0) use Latex default

    def makeChild(self):
        if self.parent != self:
            self.parent.children.append(self)
            self.parent.num_children += 1

    def getType(self):
        if self.contents.find("if") == 0 and self.contents[-1] == ":":
            return "if"
        elif self.contents.find("while") == 0 and self.contents[-1] == ":":
            return "while"
        elif self.contents.find("for") == 0 and self.contents[-1] == ":":
            return "for"
        elif self.contents == "else:":
            return "else"
        elif "=" in self.contents:
            return "io"
        else:
            return "misc"

    def drawBox(self):
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

        return '\\node (box{id}) [ {type} , {pos}] {code};\n'.format(id=self.id,
                                                                     type=boxstyle,
                                                                     pos=pos,
                                                                     code="{" + self.contents + "}")

    def drawArrows(self):
        arrows = ""
        for child in self.children:
            # If the child is older than the parent (ie feedback)
            # then the arrow takes a round shape
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
        if stopAtKeyword:
            if "if" in line or "for" in line:
                break
        numberOfLinesInLoop += 1
        a += 1
    return numberOfLinesInLoop


def findEndOfNest(raw_code, startLine):
    a = startLine + 1
    lastLineNumber = len(raw_code)
    numberOfLinesInLoop = 1

    line = raw_code[startLine]
    indentation = len(line) - len(line.lstrip())

    # Number of leading spaces in the for loop declaration
    line = raw_code[a]

    while len(line) - len(line.lstrip()) > indentation and a < lastLineNumber:
        line = raw_code[a]
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


def drawFeedback(line, boxes):
    start = boxes[line.id]
    end = findEndOfLoop(test, line.id) + line.id - 2
    boxes[end].children = []
    boxes[end].children.append(start)
    boxes[end].num_children += 1

def drawExit(line, boxes):
    end = findEndOfLoop(test, line.id) + line.id - 1
    boxes[end].offset = (-5,0)
    line.children.append(boxes[end])
    line.num_children += 1

def placeForLoop(boxes):
    for i in range(len(boxes)):
        if boxes[i].type == "for" or boxes[i].type == "while":
            boxes[i+1].offset = (5,2)
            drawFeedback(boxes[i], boxes)
            drawExit(boxes[i], boxes)

def write_latex(code):
    with open('sometexfile.tex', 'w') as f:
        f.write('\\documentclass{article}\n')
        f.write('\\usepackage{tikz}\n \\usetikzlibrary{shapes.geometric, arrows,arrows.meta, positioning, fit}\n')

        # This package lets us adjust margins
        f.write('\\usepackage[top=1.5cm, bottom=1.5cm]{geometry}')


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
    if x == 1:
        a = 4
    else:
        a = 2
    z = x + y
    return z

def test1():
    x = 1
    if x == 1:
        y = 4
        x = x**4
        x -= 5
    else:
        y = 0
        x += 1
    z = z ** 2

    for i in range(2):
        x = 4
        x += 2

    x = 3

    if z == 3:
        print("oh no")
    else:
        print("oops")

    print("hello")
    print("world")


def test3():
    x = 2
    if x == 2:
        print(x)
    else:
        x = 2
        x *= 4
    return x


boxes = []
raw_code = inspect.getsourcelines(test1)[0]

for i, line in enumerate(raw_code):
    if line.find("#"):
        line = line[:line.find("#")]
        raw_code[i] = line
    if line.strip() == "":
        del raw_code[i]

for i, line in enumerate(raw_code):
    if i == 0:
        parent = -1
    else:
        parent = boxes[i - 1]       # This assigns every line the parent of the line before it
                                    # Parents are changed later on when constructs like loops/ifs are encountered
    boxes.append(CodeLine(i, line, parent))

boxes[0].type = "start"

print("\n\n\n")

placeForLoop(boxes)

else_box_indexes = []
for i, box in enumerate(boxes):
    print(box.type)
    # Check if a box is an if statement
    if box.type == "if":
        length_if = findEndOfNest(raw_code, i) - 1

        try:
            # See if there is an else statement, and set this as a new branch of the original if block
            if boxes[i + length_if].type == "else":
                length_else = findEndOfNest(raw_code, i + length_if) - 1

                try:
                    # Sets child of last line of if statement to line after end of else statement
                    boxes[i + length_if - 1].children = [boxes[i + length_if + length_else]]
                    boxes[i + length_if + length_else].children[0].offset = (-5, length_else - length_if - 1)


                except IndexError:
                    # If there is no more code after the else statement
                    boxes[i + length_if - 1].children = []

                # Set parent of box after else to if box
                boxes[i + length_if + 1].parent = box
                boxes[i + length_if + 1].makeChild()
                boxes[i + length_if + 1].orientation = "right"
                boxes[i + length_if + 1].offset = (3, 0)

                else_box_indexes.append(i + length_if)

        except IndexError:
            pass
"""BUG - if there is not another line of code at the end of an else then an extra arrow is drawn"""

boxes = [box for i, box in enumerate(boxes) if i not in else_box_indexes]

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
