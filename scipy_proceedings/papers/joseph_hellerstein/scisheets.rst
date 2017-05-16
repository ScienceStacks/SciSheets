:author: Alicia Clark
:email: clarka34@uw.edu
:institution: University of Washington

:author: Joseph Hellerstein
:email: joseph.hellerstein@gmail.com
:institution: University of Washington
:corresponding:

--------------------------------------------------------------------------------------------------------------------
SciSheets: Delivering the Power of Programming With The Simplicity of Spreadsheets
--------------------------------------------------------------------------------------------------------------------

.. class:: abstract

Short abstract.

.. class:: keywords

   software engineering

1. Introduction
---------------

Digital spreadsheets are the "killer app" that ushered in the PC revolution.
This is largely because spreadsheets provide a conceptually simple way to do calculations that avoids the mental burdens of programming,
especially considerations of control flow, data dependencies, and data structures.
Recent estimates suggest that over 800M professionals author spreadsheet formulas as part of their work
[MODE2017],
which is about 50 times the number
of software developers world wide [Thib2013].

Despite their appeal, spreadsheets have severe shortcomings.

- poor scalability because executing formulas within the spreadsheet system has high overhead;
- great difficulty with reuse because there is no concept of encapsulation (and even different length data are problematic);
- great difficulty with transitioning from a spreadsheet to a program to facilitate integration into software systems and improve scalability;
- limited ability to handle complex data because there is no concept of structured data;
- poor readability because formulas must be expressions (not scripts) and any cell may have a formula; and
- limited ability to express calculations because formulas are limited to using a few hundred or so functions provided by the spreadsheet system (or specially coded macros).

Even with the
seriousness of these shortcomings, spreadsheets
have been
largely ignored in the computer science academic literature.
However, many innovative spreadsheet systems have been introduced.
Google Fusion Tables [Gonz2010] uses column formulas to avoid a common source of errors,
the need to copy formulas as rows are added/deleted from a table.
The Pyspread [PySpread] project uses Python as the formula language, which increases the expressiveness of formulas.
A more radical approach is taken by
the Stencila system [Stencila], which
provides a document structure that includes cells that execute formulas, including the display of of data tables;
cells may execute statements from many languages including Python and R.

Sadly, even with the aforementioned innovations in spreadsheets,
serious deficiencies remain.

1. The expressiveness of formulas is limited because formulas are restricted to being expressions, not scripts (although Stencila does provide a limited form of scripting).
2. None of the innovations ease the burden of
   dealing with complex data relationships, such as n-to-m relationships.
3. None of the innovations address code sharing and reuse between
   spreadsheet users or between spreadsheet users and software engineers.
4. Very little has been done to address the performance problems that occur as spreadsheets scale.

This paper introduces SciSheets [SciSheets], a new spreadsheet system with the goal of delivering
the power of programming with the simplicity of spreadsheets.
Our target users are technical professionals, such as scientists and financial engineers,
who do complex calculations on structured data.
To date, our focus has been on calculations,
not features such as formatting.

SciSheets addresses the deficiencies enumerated above by introducing
several novel features.

- *Formulas can be Python scripts, not just expressions.*
  This increases the expressiveness of formulas.
- *Tables can have nested columns (columns within columns).*
  This provides a conceptually simple way to express
  complex data relationships, such as n-to-m relationships.
- *Spreadsheets can be exported as standalone Python programs.*
  This provides for sharing and reuse since the exported codes
  can be used by other SciSheets spreadsheets or by
  python programs.
  This feature also improves scalability since
  calculations can be executed without the overhead of the spreadsheet system.

The remainder of this paper is organized as follows.

2. Use Cases
------------

1. User profiles

   a. Calcers - no knowledge of data types or control flow. 
      Doesn't think about data dependencies. 
      Mental model is a calculator.

   b. Scripter - Writes scripts, saving them in a file. Can do if-then, for-loop, and list data types and pandas DataFrames.

   c. Programmer - Knows about functions and modules.

Our hope is to elevate the capabilities of the first two groups, introducing calculators to the power of scripting and
scripting to the power of programming.

.. figure:: ExistingSpreadSheet.png

   Data view (top) and formulas view (bottom) for an Excel spreadsheet that calculates Michaelis-Menten Parameters. :label:`fig-excel1`

2. Michaelis-Menten

   a. Background. Common processing of biochemical assays to compute key characteristics of enzymes
   b. Use cases

      a) Writing formulas - script vs. expression
      b) Code reuse - None

.. figure:: ExcelMultiTable.png

   Student grade data from two departments in the school of engineering. :label:`fig-excel2`

3. Managing multiple tables

   a. Background. Multiple departments in the school of engineering, 
      keeping records in slightly different ways.
   b. Use cases
 
      a) View data side-by-side, but still manage as separate tables
         in terms of insert/delete


3. Addressing the Use Cases
---------------------------

.. figure:: ColumnPopup.png

   Column popup menu in a scisheet for the Michaelis-Menten calculation. :label:`fig-columnpopup`

.. figure:: SimpleFormula.png
   :scale: 50 %

   Formula for computing the inverse of the input value S. :label:`fig-simpleformula`

.. figure:: ComplexFormula.png

   Formula for computing the slope and intercept of a regression line for the Michaelis-Menten calculation. Note that One column assigns values to another column and that a script is used. label:`fig-simpleformula`

1. UI structure

   a. Elements - sheet, tables, columns, rows, cells (Fig)
   b. Popup menus
   c. Execution model: prologue, formula evaluations, epilogue. (Dependency checking is not possible
      because users can employ "eval" statement.)

.. figure:: TableExport.png

   Menu to export a table as a standalone python program. :label:`fig-export`

2. Code re-use through export

.. figure:: ProcessFiles.png
   :scale: 50 %

   A scisheet that processes many CSV files. :label:`fig-processfiles`

.. figure:: ProcessFilesScript.png

   Column formula that is a script to process CSV files. :label:`fig-processfiles`

3. Formulas can be scripts

.. figure:: Multitable.png

   A table with two subtables. :label:`fig-subtables`

.. figure:: PopupForHierarchicalRowInsert.png

   Menu to insert a row in one subtable. :label:`fig-subtable-insert`

.. figure:: AfterHierarchicalRowInsert.png

   Result of inserting a row in one subtable. :label:`fig-subtable-after`

4. Managing multiple tables

4. Design
---------


.. figure:: SciSheetsCoreClasses.png
   :scale: 30 %

   SciSheets core classes. :label:`fig-coreclasses`

1. Client-Server architecture

   a. Client (JS) - Simple UI handling 
      (popups, render table, convey user inputs via AJAX)
   b. Server (python) - table storage, formula evaluation

2. Software Dependencies - Django, JS packages

3. Class hierarchy

4. SciSheet export

5. Implications of requirements

   a. Requirements

      a.) User doesn't think about data dependencies between columns.
      b.) User can write arbitrary python scripts.

   b. Implications

      a.) Cannot do static dependency determination. Solution - execute until convergence.
      b.) Syntax and runtime errors must be isolated within the line in the column, not just to the column.

Function definition

.. code-block:: python

   def michaelis(S, V):
     from scisheets.core import api as api
     s = api.APIPlugin('michaelis.scish')
     s.initialize()
     _table = s.getTable()

Prologue

.. code-block:: python

   s.controller.startBlock('Prologue')
   # Prologue
   import math as mt
   import numpy as np
   from os import listdir
   from os.path import isfile, join
   import pandas as pd
   import scipy as sp
   from numpy import nan  # Must follow sympy import
   s.controller.endBlock()

Loop initialization

.. code-block:: python
  
   # Formula evaluation loop
   s.controller.initializeLoop()
   while not s.controller.isTerminateLoop():
     s.controller.startAnIteration()

Formula evaluation

.. code-block:: python

   #
     try:
       # Column INV_S
       s.controller.startBlock('INV_S')
       INV_S = 1/S
       s.controller.endBlock()
       INV_S = s.coerceValues('INV_S', INV_S)
     except Exception as exc:
       s.controller.exceptionForBlock(exc)
      
     try:
       # Column INV_V
       s.controller.startBlock('INV_V')
       INV_V = np.round(1/V,2)
       s.controller.endBlock()
       INV_V = s.coerceValues('INV_V', INV_V)
     except Exception as exc:
       s.controller.exceptionForBlock(exc)

Close of function

.. code-block:: python
    
   #
     s.controller.endAnIteration()
   
   if s.controller.getException() is not None:
     raise Exception(s.controller.formatError(
         is_absolute_linenumber=True))
   
   s.controller.startBlock('Epilogue')
   # Epilogue
   s.controller.endBlock()
   
   return V_MAX,K_M

Tests

.. code-block:: python

   from scisheets.core import api as api
   from michaelis import michaelis
   import unittest
   
   #############################
   # Tests
   #############################
   # pylint: disable=W0212,C0111,R0904
   class Testmichaelis(unittest.TestCase):
   
     def setUp(self):
       from scisheets.core import api as api
       self.s = api.APIPlugin('michaelis.scish')
       self.s.initialize()
       _table = self.s.getTable()
       
     def testBasics(self):
       # Assign column values to program variables.
       S = self.s.getColumnValue('S')
       V = self.s.getColumnValue('V')
       V_MAX,K_M = michaelis(S,V)
       self.assertTrue(
           self.s.compareToColumnValues('V_MAX', V_MAX))
       self.assertTrue(
           self.s.compareToColumnValues('K_M', K_M))
   
   if __name__ == '__main__':
     unittest.main()

  

5. Logging and performance

5. Future Work
--------------

- Realizing the full power of hierarchies - reuse with "copy" action but with different technical semantics.

- Graphics

- Version control

6. Conclusions
--------------


References
----------
.. [MODE2017] *MODELOFF - Financial Modeling World Championships*,
              http://www.modeloff.com/the-legend/.
.. [Thib2013] Thibodeau, Patrick. 
              *India to overtake U.S. on number of developers by 2017*, 
              COMPUTERWORLD, Jul 10, 2013.
.. [Gonz2010] *Google Fusion Tables: Web-Centered Data Management
              and Collaboration*, Hector Gonzalez et al., SIGMOD, 2010.
.. [PySpread] Manns, M. *PYSPREAD*, http://github.com/manns/pyspread.
.. [Stencila] *Stencila*, https://stenci.la/.
.. [SciSheet] *SciSheets*, https://github.com/ScienceStacks/SciSheets.
