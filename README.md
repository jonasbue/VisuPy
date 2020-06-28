# VisuPy

Have you ever written code in the past which you come back to later and you can't understand what it does? Our project aims to fix this. Flowcharts are important in the early stages of program design as a neat way of representing how the program will work, but we think they can be important all the way through development. 

Visupy takes a Python function and automatically generates a flowchart, so the developer can more clearly visualise what their program is doing and try to make sense of it. As Visupy outputs to Latex, it can also be used for students and researchers to embed code in their papers in an easy to follow and visually appealing way. Visupy is designed as an accessible visualisation tool specifically for maths/physics students, who may not have as much programming knowledge and require a simple way to see what their code does. 

## How to use

To run VisuPy, be sure to have LaTeX installed.
Then, in your Python script, run the following to visualize your function in a LaTeX flowchart:

import visupy

visupy.visualize(function, 'filename')
