# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
# Relief from the License may be granted by purchasing a commercial license.
"""Lattice Function String Sample Data"""


def lattice_functions():
    """Dispatches Sample List"""
    lattice_functions_list = {
        "files": [
            """"@ct.lattice arr = array.array('i', [1, 2, 3]) # printing original array print ("The new created array is : ",end="") for i in range (0,3): print (arr[i], end=" ") print ("\r")""",
            """@ct.lattice import numpy as geek b = geek.zeros(2, dtype = int) print("Matrix b : \n", b) a = geek.zeros([2, 2], dtype = int) print("\nMatrix a : \n", a) c = geek.zeros([3, 3]) print("\nMatrix c : \n", c)""",
            """@ct.lattice import numpy # initializing matrices x = numpy.array([[1, 2], [4, 5]]) y = numpy.array([[7, 8], [9, 10]]) # using add() to add matrices print ("The element wise addition of matrix is : ") print (numpy.add(x,y)) # using subtract() to subtract matrices print ("The element wise subtraction of matrix is : ") print (numpy.subtract(x,y)) # using divide() to divide matrices print ("The element wise division of matrix is : ") print (numpy.divide(x,y)) print("\nMatrix a : \n", a) c = geek.zeros([3, 3]) print("\nMatrix c : \n", c)""",
            """@ct.lattice from tkinter import * from tkinter.ttk import * from time import strftime # creating tkinter window root = Tk() # Adding widgets to the root window Label(root, text = 'GeeksforGeeks', font =('Verdana', 15)).pack(side = TOP, pady = 10) Button(root, text = 'Click Me !').pack(side = TOP) mainloop() # using add() to add matrices print ("The element wise addition of matrix is : ") print (numpy.add(x,y)) # using subtract() to subtract matrices print ("The element wise subtraction of matrix is : ") print (numpy.subtract(x,y)) # using divide() to divide matrices print ("The element wise division of matrix is : ") print (numpy.divide(x,y)) print("\nMatrix a : \n", a) c = geek.zeros([3, 3]) print("\nMatrix c : \n", c)""",
            """@ct.lattice import pandas as pd # Define a dictionary containing employee data data = {'Name':['Jai', 'Princi', 'Gaurav', 'Anuj'], 'Age':[27, 24, 22, 32], 'Address':['Delhi', 'Kanpur', 'Allahabad', 'Kannauj'], 'Qualification':['Msc', 'MA', 'MCA', 'Phd']} # Convert the dictionary into DataFrame df = pd.DataFrame(data) # select two columns print(df[['Name', 'Qualification']]) # Adding widgets to the root window Label(root, text = 'GeeksforGeeks', font =('Verdana', 15)).pack(side = TOP, pady = 10) Button(root, text = 'Click Me !').pack(side = TOP) mainloop() # using add() to add matrices print ("The element wise addition of matrix is : ") print (numpy.add(x,y)) # using subtract() to subtract matrices print ("The element wise subtraction of matrix is : ") print (numpy.subtract(x,y)) # using divide() to divide matrices print ("The element wise division of matrix is : ") print (numpy.divide(x,y)) print("\nMatrix a : \n", a) c = geek.zeros([3, 3]) print("\nMatrix c : \n", c)""",
            """@ct.lattice import pandas as pd # making data frame from csv file data = pd.read_csv("nba.csv", index_col ="Name") # retrieving multiple columns by indexing operator first = data[["Age", "College", "Salary"]] 'Qualification':['Msc', 'MA', 'MCA', 'Phd']} # Convert the dictionary into DataFrame df = pd.DataFrame(data) # select two columns print(df[['Name', 'Qualification']]) # Adding widgets to the root window Label(root, text = 'GeeksforGeeks', font =('Verdana', 15)).pack(side = TOP, pady = 10) Button(root, text = 'Click Me !').pack(side = TOP) mainloop() # using add() to add matrices print ("The element wise addition of matrix is : ") print (numpy.add(x,y)) # using subtract() to subtract matrices print ("The element wise subtraction of matrix is : ") print (numpy.subtract(x,y)) # using divide() to divide matrices print ("The element wise division of matrix is : ") print (numpy.divide(x,y)) print("\nMatrix a : \n", a) c = geek.zeros([3, 3]) print("\nMatrix c : \n", c)""",
        ]
    }

    return lattice_functions_list
