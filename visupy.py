import inspect
import string
import subprocess, os
from sys import platform


class CodeLine:
    def __init__(self, id, contents, parent, flagInLoop=None):
        """Creates a new CodeLine object.
        id is the line number in the function.
        type can be: start, io, if, else, for, while, misc
        contents is the string with the code for this line
        """

        self.id = int(id)               # Line number
        self.contents = str(contents.strip())

        if flagInLoop is None:
            self.flagInLoop = {}     # are we in a if loop - need to give options of if and no else.
        else:
            self.flagInLoop = flagInLoop

        self.type = self.getType()
        # We want to check if the parent was a if loop


        self.parent = parent if parent != -1 else self  # Parent box. Set to self if no parent (i.e. start)
        self.makeChild()

        self.childOfIf = None  # for line arrow annotation


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
            #self.flagInLoop.update({'if':'start'})
            return "if"
        elif self.contents.find("while") == 0 and self.contents[-1] == ":":
            return "while"
        elif self.contents.find("for") == 0 and self.contents[-1] == ":":
            self.flagInLoop.update({'for':'head'})
            return "for"
        elif self.contents == "else:":
            return "else"
        elif self.contents.lower() == "end":
            return "end"
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
        elif self.type == "end":
            boxstyle = "startstop"
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
            if child.childOfIf and self.type== 'if':

                anchor = '[anchor='
                if child.orientation == 'below':
                    anchor += 'east]'
                if child.orientation == 'right':
                    anchor += 'south]'
                arrows += '\draw [arrow] (box{id}) -- node {orien} {text} (box{child});\n'.format(id=self.id, orien=anchor, text='{' + child.childOfIf + '}', child=child.id)

            elif self.id > child.id:
                arrows += '\draw [arrow] (box{id}) to [bend left] (box{child});\n'.format(id=self.id, child=child.id)
            else:
                arrows += '\draw [arrow] (box{id}) -- (box{child});\n'.format(id=self.id, child=child.id)
        return arrows


def findIndentation(line):
    return len(line) - len(line.strip())


# Finds the number of lines in a loop, excluding the declaration line
def findEndOfLoop(function, startLine):
    a = startLine + 1
    lastLineNumber = len(inspect.getsourcelines(function)[0])
    numberOfLinesInLoop = 1

    line = inspect.getsourcelines(function)[0][startLine]
    indentation = len(line) - len(line.lstrip())

    # Number of leading spaces in the for loop declaration
    line = inspect.getsourcelines(function)[0][a]

    while len(line) - len(line.lstrip()) > indentation and a < lastLineNumber:
        line = inspect.getsourcelines(function)[0][a]
        numberOfLinesInLoop += 1
        a += 1
    return numberOfLinesInLoop


def findEndOfNest(raw_code, startLine):
    a = startLine + 1
    lastLineNumber = len(raw_code)
    numberOfLinesInLoop = 0

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


def drawFeedback(line, boxes, function):
    end = findEndOfLoop(function, line.id) + line.id - 2
    boxes[end].children = []
    boxes[end].children.append(line)
    boxes[end].num_children = 1

def drawExit(line, boxes, function):
    end = findEndOfLoop(function, line.id) + line.id - 1
    line.children.append(boxes[end])
    line.num_children += 1
    boxes[end].offset = (-5,0)

def placeForLoop(boxes, function):
    for i in range(len(boxes)):
        if boxes[i].type == "for" or boxes[i].type == "while":
            boxes[i+1].offset = (5,2)
            drawFeedback(boxes[i], boxes, function)
            drawExit(boxes[i], boxes, function)

def write_latex(code, filename):
    with open(filename+'.tex', 'w') as f:
        f.write('\\documentclass{article}\n \\usepackage[a3paper]{geometry}\n\\pagestyle{empty}\n')
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

        f.write(code)

        f.write('\\end{tikzpicture}\n')
        f.write('\\end{document}\n')

def printOGCode(code):
    print('\nOriginal Code: \n===========\n')
    print(code)
    print('===========\n')

# BUG: If there is a line break anywhere before a for loop,
# then the for loop will not render properly



def visualize(function, filename='visualize', quiet=True):
    boxes = []
    raw_code = inspect.getsourcelines(function)[0]
    printOGCode(inspect.getsource(function))
    raw_code.append("END")

    for i, line in enumerate(raw_code):
        if line.strip() == "":
            del raw_code[i]

    for i, line in enumerate(raw_code):
        if i == 0:
            parent = -1
        else:
            parent = boxes[i - 1]       # This assigns every line the parent of the line before it
                                        # Parfunctionents are changed later on when constructs like loops/ifs are encountered
        boxes.append(CodeLine(i, line, parent))
    print('')
    boxes[0].type = "start"


    placeForLoop(boxes, function)

    else_box_indexes = []
    for i, box in enumerate(boxes):
        # Line must know they are in a for loop
        # After for loop circle back to for init and exit

        #maybe generalize using id?
        if box.type=='for':

            length_for = findEndOfNest(raw_code, i)  # line in for loop inc. def.
            # for lines in for loop (exc. def)
            for frline in range(i,  length_for+i):
                boxes[frline].flagInLoop.update({'for':i})

            # so frline+1 should be where we exit the for loop
            boxes[frline+1].parent = boxes[i]
            boxes[i].makeChild()
            boxes[i].children.extend([boxes[frline+1]])




        # Check if a box is an if statement
        if box.type == "if":


            #print(boxes[i+1].contents)
            # first line coming out of an if, label arrow true
            boxes[i+1].childOfIf = 'True'
            length_if = findEndOfNest(raw_code, i)


            if boxes[i].flagInLoop.get('for') is not None and box.flagInLoop.get('for', None) is not 'head':
                retBox = box.flagInLoop.get('for')
            else:
                retBox = None  
            try:
                # See if there is an else statement, and set this as a new branch of the original if block
                if boxes[i + length_if].type == "else":

                    # you are the else child from an if
                    boxes[i + length_if + 1].childOfIf =  'Else'
                    length_else = findEndOfNest(raw_code, i + length_if)
                    
                    # Sets child of last line of if statement to line after end of else statement
                    if retBox is not None:
                        boxes[i + length_if - 1].children = [boxes[retBox]]
                    else:
                        boxes[i + length_if - 1].children = [boxes[i + length_if + length_else]]
                    boxes[i + length_if + length_else -1].children[0].offset = (-5, 2*(length_else - length_if - 1))

                    # Set parent of box after else to if box
                    boxes[i + length_if + 1].parent = boxes[i]
                    boxes[i + length_if + 1].makeChild()
                    boxes[i + length_if + 1].orientation = "right"
                    boxes[i + length_if + 1].offset = (3, 0)

                    else_box_indexes.append(i + length_if)
                else: # must be a true
                    # end the if path so true/false ends at the same place
                    boxes[i+length_if].parent = boxes[i]
                    boxes[i].makeChild()
                    boxes[i].children.extend([boxes[i+length_if]])

                    boxes[i+length_if].offset = (4,0)
                    
                    boxes[i+length_if].childOfIf = 'False'
            except IndexError:
                print('IndexError')

    # D
    boxes = [box for i, box in enumerate(boxes) if i not in else_box_indexes]

    string = ""

    for box in boxes:
        string += box.drawBox()

    for box in boxes:
        string += box.drawArrows()

    write_latex(string, filename)
    s= "pdflatex ./"+filename+".tex"
    if quiet == True:
        s = "pdflatex -interaction=batchmode  ./"+filename+".tex"
    x = os.system(s)
    if x != 0:
        print('Exit-code not 0, check result!')
    else:
        ps = filename+'.pdf'
        if platform == "linux" or platform == "linux2":
            os.system('xdg-open ' + ps)

        elif platform == "darwin":
            os.system('open '+ ps)

        elif platform == 'win32':
            os.system('start ' + ps)



