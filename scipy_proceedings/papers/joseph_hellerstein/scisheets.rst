:author: Alicia Clark
:email: clarka34@uw.edu
:institution: Department of Mechanical Engineering, University of Washington

:author: Joseph Hellerstein
:email: joseph.hellerstein@gmail.com
:institution: eScience Institute, University of Washington
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
This is largely because spreadsheets provide a conceptually simple way to do calculations that
(a) closely associates data with the calculations that produce the data and 
(b) avoids the mental burdens of programming
such as
control flow, data dependencies, and data structures.
Estimates suggest that over 800M professionals author spreadsheet formulas as part of their work
[MODE2017],
which is about 50 times the number
of software developers world wide [THIB2013].

We categorize
spreadsheet users as follows:

- **Novices** want to evaluate equations, but they do not want
  to think about how to do it.
  Spreadsheet formulas work well for Novices since: (a) they can
  ignore data dependencies;
  (b) they can avoid flow control by using
  "copy" and "paste" for iteration;
  and (c) data structures are "visual" (e.g., rectangular blocks).
- **Scripters** feel comfortable with expressing calculations algorithmically using ``for`` and ``if``
  statements; and they can use simple data structures such as lists and
  ``pandas DataFrames`` (which are like spreadsheets).
  However, they rarely encapsulate code into functions,
  preferring to ``copy`` and ``paste`` code to get reuse.
- **Programmers** know about sophisticated data structures, modularization, reuse, and testing.

Our experience is primarily with scientists, especially biologists and chemists.
Most commonly, we encounter Novices and Scripters.
Only Programmers take advantage of spreadsheet macro capabilities
(e.g.,  Visual Basic for Microsoft Excel or
AppScript in Google Sheets).

Based on this experience, we find
existing spreadsheets lack several key requirements.
The first requirement is **Expressivity**.
Existing spreadsheets only support formulas that are expressions,
not scripts.
This is significant limitation for Scripters
who often want to express calculations as algorithms.
It is also a burden for Novices
who want to write linear workflows to
articulate a computational recipe, a kind
a computational laboratory notebook.
A second requirement not addressed in today's spreadsheets is
**Reuse**.
Specifically, it is impossible to reuse spreadsheet
formulas in other spreadsheet formulas or in software systems.
A third requirement that is missing from existing spreadsheets
is handling
**Complex Data**.
For example, today's spreadsheets
make it extremely difficult to manipulate
hierarchically structured data and n-to-m relationships.
A final requirement we consider is
**Performance**.
A common complaint is that
spreadsheets scale poorly with
the size of data and the number of formulas.

Academic computer science has recognized the growing importance
of end-user programming (EUP) [BURN2009].
Even so,
there is little
academic literature on spreadsheets.
[MCLU2006] discusses object oriented spreadsheets that
introduces a sophisticated object model but fails to recognize
the requirements of Novices to have a simple way to evaluate equations.
[JONE2003] describes a way that users can implement functions
within a spreadsheet to get reuse, but the approach requires
considerable user effort and does not address reuse of
spreadsheet formulas in a larger software system.
Outside of academia there has been significant
interest in innovating spreadsheets.
Google Fusion Tables [GONZ2010]
and the "Tables" feature of Microsoft Excel ref??
use column formulas to avoid a common source of errors,
the need to copy formulas as rows are added/deleted from a table.
The Pyspread [PYSPREAD] project uses Python as the formula language, which gives formulas access to thousands of Python packages.
A more radical approach is taken by
STENCILA [STENCILA],
a document system that provides ways to execute code that
updates tables (an approach that is in the same
spirit as Jupyter Notebooks
[PERE2015]).
STENCILA supports a variety of languages including
JavaScript, Python, and SQL.
However, STENCILA lacks features that spreadsheet users expect:
(a) closely associating data with the calculations that produce the data
and (b) avoiding considerations of data dependencies in calculations.

This paper introduces SciSheets [SCISHEETS], 
a new spreadsheet system with the
objective of delivering
the power of programming with the simplicity of spreadsheets.
The name SciSheets is a contraction of the phrase "Scientific Spreadsheet", a nod to the users
who motivated the requirements that we address.
That said,
our target users are more broadly technical professionals
who do complex calculations on structured data.
We use the term **scisheet** to refer to a SciSheets spreadsheet.
We note in passing that our focus for scisheets is on
calculations,
not document processing features such as formatting and drawing figures.

SciSheets addresses the above requirements by introducing
several novel features.

- *Formula Scripts.*
  Scisheet formulas can be Python scripts, not just expressions.
  This addresses the expressivity requirement since
  calculations can be expressed as algorithms.
- *Program Export.*
  Scisheets can be exported as standalone Python programs.
  This addresses the reuse requirement since
  exported spreadsheets
  can be reused in SciSheets formulas and/or by
  external programs (e.g., written by Programmers).
  Further, performance is improved by the export feature
  since calculations can execute without the
  overheads of the spreadsheet environment.
- *Subtables.*
  Tables can have columns that are themselves tables (columns within columns).
  This addresses the complex data requirement,
  such as representing n-to-m relationships.

The remainder of the paper is organized as follows.
Section 2 describes the requirements that we consider, and
Section 3 details the SciSheets features that address these requirements.
The design of SciSheets is discussed in Section 4, and
Section 5 discusses features planned for SciSheets.
Our conclusions are presented in Section 6.

2. Requirements
---------------

This section presents examples that motivate
the requirements of expressivity, reuse, and complex data.

Our first example is drawn from biochemistry labs
studying enzyme mediated chemical reactions.
Commonly, the Michaelis-Menten ref?? Model of enzyme activity is used in which
there is a single chemical species, called the substrate, that interacts with the enzyme to produce
a new chemical species (the product).
Two properties of enzymes are of much interest: the maximum reaction rate,
denoted by :math:`V_{MAX}`, and the concentration :math:`K_M` of substrate that achieves
a reaction rate equal to half of :math:`V_{MAX}`.

To perform the Michaelis-Menten analysis,
laboratory data are collected for different values of the substrate concentration
:math:`S` and reaction rate :math:`V`.
Then, a calculation is done to obtain the parameters :math:`V_{MAX}` and :math:`K_M`
using the following recipe.

1. Compute :math:`1/S` and :math:`1/V`, the inverses of :math:`S` and :math:`V`.
2. Compute the intercept and slope of the regression of :math:`1/V` on
   :math:`1/S`.
3. Calculate :math:`V_{MAX}` and :math:`K_M` from the intercept and slope.

.. figure:: excel1.png

   Data view for an Excel spreadsheet that calculates Michaelis-Menten Parameters. :label:`fig-excel1`

.. figure:: excel2.png

   Formulas used in Fig. :ref:`fig-excel1`. :label:`fig-excel2`

.. figure:: ExcelMultiTable.png

   Student grade data from two departments in the school of engineering.
   CSE and Biology are separate tables that are grouped together for
   convenience of analysis.
   However, it is difficult to manage them separate, such as insert, delete,
   and/or hide rows.
   :label:`fig-complexdata`

Fig. :ref:`fig-excel1` shows an Excel spreadsheet that implements this recipe
with column names chosen to correspond to the variables in the recipe.
Fig. :ref:`fig-excel2` shows the formulas that
perform these calculations.
Readability can be improved by using column formulas (e.g., as in Fusion Tables).
However, two problems remain.
Novices cannot *explicitly* articulate
the computational recipe; rather, the recipe is implicit in the order of the columns.
Even more serious, there is no way to reuse these formulas in other
formulas (other than error-prone copy-and-paste), and
there is no way
to reuse formulas in an external program.

We consider a second example to illustrate problems with handling
non-trivial data relationships in spreadsheets.
Fig. :ref:`fig-complexdata` displays data that a university
might have for students in two departments in the School of Engineering.
The data are organized into two tables (CSE and Biology) grouped under
the School of Engineering, with separate columns for student identifiers
and grades.
These tables
are adjacent to each other to facilitate the comparisons between
students.
However, the tables are independent of each other
in that we should be able to insert, delete, and hide rows
in one table without affecting
the other table.
Unfortunately, existing spreadsheet systems do not handle this well in that adding
a row to one table affects all tables on that row in the sheet.
Note that arranging the tables vertically does not help since now the problem
becomes adding, deleting, or hiding columns.
(We could arrange the tables in a diagonal, but
this makes it difficult to make visual comparisons between
tables.)

3. Features
-----------

This section describes SciSheets features that address the requirements of expressivity, reuse, complex data,
and performance.
We begin with a discussion of the SciSheets
user interface in Section 3.1.
Then, Sections 3.2, 3.3, and 3.4 in turn present:
formula scripts (which addresses expressivity),
program export (which addresses reuse and performance),
and subtables (which addresses complex data).

3.1 User Interface
~~~~~~~~~~~~~~~~~~

.. figure:: ColumnPopup.png

   Column popup menu in a scisheet for the Michaelis-Menten calculation. :label:`fig-columnpopup`

Fig. :ref:`fig-columnpopup` displays a scisheet that performs the Michaelis-Menten calculations
as we did in Fig. :ref:`fig-excel1`.
A scisheet
has the familiar tabular structure of a spreadsheet.
However, unlike spreadsheets, SciSheets knows about the
*structure of a scisheet:
scisheet (entire sheet), tables, columns, rows, and cells*.
Table and column names are Python variables that the user can reference in formulas.
These **Column Variables**
are ``pandas Arrays``.
It is easy to do vector calculations on Column Variables using a rich set of operators that properly handle
missing data using `nan` values.

Users interact directly with scisheet elements (instead of primarily with a menu, as is done in spreadsheet systems).
A left click on a scisheet element results in a popup menu.
For example,
in Fig. :ref:`fig-columnpopup` we see the column popup for the column ``INV_S``.
Users select an item from the popup, and this may in turn present additional menus.
The popup menus for row, column, and table have common items for insert, delete, hide/unhide.
Columns additionally have a formula item.
The scisheet popup has items for saving and renaming the scisheet as well as undoing/redoing operations
on the scisheet.
The cell popup is an editor for the value in the cell.


.. figure:: SimpleFormula.png
   :scale: 50 %

   Formula for computing the inverse of the input value S. :label:`fig-simpleformula`

Fig. :ref:`fig-simpleformula` displays the submenu resulting from selecting the formula item
from the popup menu in Fig. :ref:`fig-columnpopup` for the column ``INV_S``.
A simple line editor is displayed.
The formula is an expression that references the Column Variable ``S``.
A column that contains a formula has its name annotated with an ``*``.

3.2 Formula Scripts
~~~~~~~~~~~~~~~~~~~

.. figure:: ComplexFormula.png

   Formula for the complete calculation of :math:`V_{MAX}` and
   :math:`K_M`.
   The formula is a simple script, allowing a Novice to see
   exactly how the data in the scisheet are produced.
   Note that the formula assigns values to other columns.
   :label:`fig-complexformula`

SciSheets allows formulas to be scripts.
For example, Fig. :ref:`fig-complexformula` displays a script that contains
the entire computational recipe for the Michaelis-Menten calculation
described in Section 2.
This capability greatly increases the ability of spreadsheet users
to describe and document their calculations.

At this point, we elaborate briefly on how formula evaluation is done
in SciSheets.
Since a formula may contain arbitrary Python expressions including
``eval`` expressions, we cannot use static dependency analysis
to determine data dependencies.
Thus, formula evaluation is done iteratively.
But how many times must this iteration be done?

Consider an evaluation of *N* formula columns assuming that
there are no
circular references or other inherent anomalies in the formulas.
Then, at most *N* iterations are needed to converge since on each iteration
at least one Column Variable is assigned its value.
If after *N* iterations, there is an exception, (e.g., a Column Variable
does not have a value assigned), this is reported to the user since there is
an error in the formulas.
Otherwise, the scisheet is updated with the new values of the
Column Variables.
Actually, we can do better than this since
if the values of Column Variables converge after loop iteration
*M < N* (and there is no exception), then
formula evaluation stops.

SciSheets augments formula evaluation by providing users with the opportunity
to specify two additional formulas.
The **Prologue Formula** is executed once at the beginning of formula evaluation;
the **Epilogue Formula** is executed once at the end of formula evaluation.
These formulas provide a way to do high overhead operations in a one-shot manner
and so providing another feature
related to the Performance requirement.
For example, a user may have Prologue Formula that
reads a file (e.g., to initialize input values in a table) at the beginning
of the calculation, and an Epilogue Formula
that writes results at the end of the calculation.
Prologue and Epilogue Formulas are modified through the scisheet popup menu.

3.3. Program Export
~~~~~~~~~~~~~~~~~~~

.. figure:: TableExport.png

   Menu to export a table as a standalone python program. :label:`fig-export`

A scisheet can be executed as a standalone program as
a function in a python module.
The feature addresses the Reuse requirement since
exported programs can be used in scisheet formulas
and/or external programs.
The export feature also addresses the Performance requirement
since executing code standalone eliminates the overheads of
the spreadsheet environment.

Fig. :ref:`fig-export` displays the scisheet popup menu for
program export.
The user sees a menu with entries for the function name,
inputs (list of column names that are inputs),
and outputs (list of column names that are computed by the function).

Program export produces two files.
The first is the python module containing the exported function.
The second is a python file containing a test for the exported function.

We begin with the first file.
The code in this file is structured into several sections:

- Function definition and setup
- Formula evaluation
- Function close

The function definition and setup contains the function definition,
imports, and the scisheet Prologue Formula (a script consisting of imports).

.. code-block:: python

   # Function definition
   def michaelis(S, V):
     from scisheets.core import api as api
     s = api.APIPlugin('michaelis.scish')
     s.initialize()
     _table = s.getTable()
     # Prologue
     s.controller.startBlock('Prologue')
     # Begin Prologue
     import math as mt
     import numpy as np
     from os import listdir
     from os.path import isfile, join
     import pandas as pd
     import scipy as sp
     from numpy import nan  # Must follow sympy import
     # End Prologue
     s.controller.endBlock()

In the above code, there is an import of ``api`` from ``scisheets.core``.
``api`` is the SciSheets runtime.
The API object ``s`` is constructed from the
exported scisheet that is
is serialized in a JSON format
with extension ``.scish``.

This code points to a somewhat subtle requirement that SciSheets addresses.
We refer to this as the **Script Debuggability** requirement,
a requirement that arises because allowing a formula to be script
means that errors must be localized to a line within the formula.
SciSheets handles this through the use of the paired statements
``s.controller.startBlock('Prologue')``
and
``s.controller.endBlock()``.
These statements allow
the SciSheets API as to identify which formula is being executed
so that formula errors can be localized to a particular line.


Next, we consider formula evaluation.

.. code-block:: python

     # Loop initialization
     s.controller.initializeLoop()
     while not s.controller.isTerminateLoop():
       s.controller.startAnIteration()
       # Formula evaluation blocks
       try:
         # Column INV_S
         s.controller.startBlock('INV_S')
         INV_S = 1/S
         s.controller.endBlock()
         INV_S = s.coerceValues('INV_S', INV_S)
       except Exception as exc:
         s.controller.exceptionForBlock(exc)


``s.controller.initializeLoop()`` snapshots Column Variables.
``s.controller.isTerminateLoop()`` counts loop iterations, looks
for convergence of Column Variables, and checks to see if the last
loop iteration had an exception.
For each formula column, there is a ``try except`` block that informs
the API as to the formula being executed, executes the formula,
and records any exception.
Note that loop execution continues even if there is an execution
for a formula column; this is essential if formula columns are not
ordered according to their data dependencies.

Last, there is the function close.
Here, the loop termination condition is checked.
The occurrence of an exception formula evaluation causes an exception
with the line number in the formula in which the (last) exception occurred.
If there is no exception, then Epilogue Formula is executed,
and the output values of the function are returned.

.. code-block:: python

       # Close of function
       s.controller.endAnIteration()

     if s.controller.getException() is not None:
       raise Exception(s.controller.formatError(
           is_absolute_linenumber=True))

     s.controller.startBlock('Epilogue')
     # Epilogue
     s.controller.endBlock()

     return V_MAX,K_M

The test code makes use of ``unittest`` with a ``setUp``
method that assigns ``self.s`` the value of an API object.
The test is to compare the results of running the
exported function on columns in the scisheet that are
input to the function with the values of columns
that are outputs from the function.

.. code-block:: python

     def testBasics(self):
       # Assign column values to program variables.
       S = self.s.getColumnValue('S')
       V = self.s.getColumnValue('V')
       V_MAX,K_M = michaelis(S,V)
       self.assertTrue(
           self.s.compareToColumnValues('V_MAX', V_MAX))
       self.assertTrue(
           self.s.compareToColumnValues('K_M', K_M))

.. figure:: ProcessFiles.png
   :scale: 50 %

   A scisheet that processes many CSV files. :label:`fig-processfiles`

.. figure:: ProcessFilesScript.png

   Column formula for ``K_M`` in
   Fig. :ref:`fig-processfiles` that is a script to process a
   list of CSV files.
   :label:`fig-processfilesscript`

The combination of the program export and formula script features is very powerful.
For example, the ``michaelis`` function exported in
Fig. :ref:`fig-processfiles` reuses the ``michaelis`` function to process a list of files.
Fig. :ref:`fig-processfilesscript` displays the column formula for ``K_M``.

3.4. Subtables
~~~~~~~~~~~~~~

Subtables provide a way for SciSheets to deal with complex data.
This feature allows for having tables nested within a table.

.. figure:: Multitable.png

   A table with two subtables.
   Subtables CSE and Biology can be manipulated separately.
   :label:`fig-subtables`

We illustrate this by revisiting the example
in Fig. :ref:`fig-complexdata`.
Fig. :ref:`fig-subtables` displays a scisheet for these data that
is similar to
Fig. :ref:`fig-complexdata`.
However, there is an importance.
*SciSheets treats
``CSE`` and ``Biology`` as independent tables.*

.. figure:: PopupForHierarchicalRowInsert.png

   Menu to insert a row in one subtable.
   The menu is accessed by left-clicking on the "3" cell
   in the column labelled "row" in the CSE subtable.
   :label:`fig-subtable-insert`

.. figure:: AfterHierarchicalRowInsert.png

   Result of inserting a row in one subtable.
   Note that a row is inserted in the CSE subtable without affecting
   the Biology substable.
   :label:`fig-subtable-after`

To see this,
recall that in Section 2
we could not insert a row into ``CSE``
without also inserting a row into ``Biology``.
SciSheets addresses this requirement by providing a row popup
for each table.
This is shown in
Fig. :ref:`fig-subtable-insert` where there is a popup
for row 3 of ``CSE``.
The result of selecting ``insert`` is displayed in
Fig. :ref:`fig-subtable-after`.
Note that the ``Biology`` subtable is not modified.

4. Design
---------

SciSheets uses a client-server design.
The client runs in the browser using HTML and JavaScript;
the server runs Python using the Django frameworki ref??.
This design provides benefits, especially
zero install deployment and
leverage the rapid pace of innovation of browser technologies.

Our strategy has been to limit the scope of the client codes
to presentation and handling end-user interactions.
The client's scisheets is limited to handling interactions to
recognize which scisheet element is clicked and to providing
menus in response to clicks.
When additional data are required to populate a menu (e.g.,
the scisheet "open" item), the client uses AJAX to obtain
information from the server.
In general, AJAX calls specify
a scisheet element (e.g., column), its name, an action to perform
(e.g., rename), and arguments.

.. figure:: SciSheetsCoreClasses.png
   :scale: 30 %

   SciSheets core classes. :label:`fig-coreclasses`

The SciSheets server handles the details of requests, which also
requires maintaining the data associated with scisheets.
Fig :ref:`fig-coreclasses` displays the core
classes used in the SciSheets server.
Core classes have several required methods.
One example of this is the ``copy`` method.
This method makes a copy of the object for which it is
invoked.
To do this, the method calls the ``copy`` method for its parent
class as well (which in turn calls its parent, and so on).
Further, the object must call the ``copy`` method for its children
if there is a has-a relationship, such as between
``ColumnContainer`` and ``Column``.
Other examples of required methods are:

- ``isEquivalent`` tests if the current object has the same
   instance values as its children
- ``getSerializationDict``
- ``deserialize``

1. Common methods for classes: copy, isEquivalent, getSerializationDict, deserialize
2. coerce method for value
3. recursive operation of copy, isEquivalent, getSerializtionDict, deserialize
4. What each level in the hierarchy does

Last, we consider performance.
Our experience is that
there are two common
causes of poor performance
in our current implementation of SciSheets.
The first relates to data size since
since, at present,
SciSheets embeds data with the
HTML document that is rendered by the browser.
We expect to address this by implementing
a feature
whereby data are downloaded on demand and
cached locally.

The second cause of poor performance is having
many iterations of the formula evaluation loop.
If there is more than one formula column, then the best case is to
evaluate each formula column twice.
The first execution produces the desired result
(which is possible
if the formula columns are in order of their data
dependencies);
the second execution confirms that the result has
converged.
Some efficiencies can be gained by using the Prologue and
Epilogue features for one-shot
execution of high overhead operations (e.g., file I/O).
Also, we are exploring the extent to which SciSheets
can detect automatically when static dependency checking
is possible so that formula evaluation is done
only once.

Clearly, performance can be improved by reducing the number
of formula columns since this reduces the maximum number
of iterations of the formulation evaluation loop.
SciSheets supports this strategy by permitting
formulas to be scripts.
This is a reasonable strategy for a Scripter, but
it may work poorly for a Novice who is unaware
of data dependencies.


5. Future Directions
--------------------

5.1 Subtables with Scoping
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Approach to reuse

5.2 Plotting
~~~~~~~~~~~~

- **Plotting** requirement.

5.3 Multiple Languages
~~~~~~~~~~~~~~~~~~~~~~

5.4 Github Integration
~~~~~~~~~~~~~~~~~~~~~~

.. figure:: spreadsheet_branch.png

   Diagram showing how a scisheet can be split into two separate branches for testing
   code features. :label:`fig-branch`

.. figure:: spreadsheet_merge.png

   Diagram showing how two scisheets will be merged (assuming no merge conflicts).
   :label:`fig-merge`

A common problem with spreadsheets is that calculations are difficult to reproduce
because some steps are manual (e.g., menu interactions) and the presence
of errors.
We refer to this as the **Reproducibility Requirement**.
Version control is an integral part of reproducibility.
Today, a spreadsheet file as a whole can be version controlled,
but this granularity is too course.
More detailed version control can be done manually.
However, this is error prone, and it is very difficult
to keep current (a considerably problem in a collaborative environment).
One automated approach is a revision history, such as
Google Sheets.
But this technique fails to record the sequence in which changes were made, by whom,
and for what reason.

It turns out that the way that SciSheets serialization of tables naturally lends itself
to github integration.
scisheets are serialized as JSON files with separate lines used for data, formulas,
and the structural relationships between columns, tables, and the scisheet.
Although the structural relationships have a complex representation, it
does seem that the SciSheets can be integrated with the line oriented version
control of github.

We are in the process of designing a user friendly integration of SciSheets with
github.
The scope here includes the following use cases:

- Branching.
  Uses should be able to create branches to explore new calculations and features
  of a scisheet.
  As with branching for software teams, branching with a spreadsheet
  should allow collaborators to work on their part of the project without
  worrying about affecting the work of others.

- Merging.

6. Conclusions
--------------

We developed SciSheets to address deficiencies
in existing spreadsheet systems.

1. Discuss entries in table. For now, performance is not evaluated.

2. SciSheets seeks to improve the programming skills of its users.
It is hoped that Novices will start using scripts,
and that Scripters will gain
better insight into modularization and testing.


.. table:: Summary of requirements
           and SciSheets features that address these requirements.
           Features in italics are planned but not yet implemented.
           :label:`fig-benefits`

   +---------------------------+--------------------------------+
   |      Requirement          |    SciSheets Feature           |
   +===========================+================================+
   | - Expressivity            | - Python formulas              |
   |                           | - Formula scripts              |
   +---------------------------+--------------------------------+
   | - Reuse                   | - Program export               |
   |                           | - *Subtables with Scoping*     |
   +---------------------------+--------------------------------+
   | - Complex Data            | - Subtables                    |
   +---------------------------+--------------------------------+
   | - Performance             | - Progam export                |
   |                           | - Prologue, Epilogue           |
   |                           | - *Load data on demand*        |
   |                           | - *Conditional static*         |
   |                           |   *dependency checking*        |
   +---------------------------+--------------------------------+
   | - Plotting                | - *Embed bokeh components*     |
   +---------------------------+--------------------------------+
   | - Script Debuggability    | - Localized exceptions         |
   +---------------------------+--------------------------------+
   | - Reproducibility         | - ``github`` *integration*     |
   +---------------------------+--------------------------------+


References
----------
.. [BURN2009] Burnett, M. *What is end-user software engineering and why does
              it matter?*, Lecture Notes in Computer Science, 2009
.. [GONZ2010] *Google Fusion Tables: Web-Centered Data Management
              and Collaboration*, Hector Gonzalez et al., SIGMOD, 2010.
.. [JONE2003] Jones, S., Blackwell, A., and Burnett, M. i
              *A user-centred approach to functions in excel*,
              SIGPLAN Notices, 2003.
.. [MCCU2006] McCutchen, M., Itzhaky, S., and Jackson, D.*Object spreadsheets:
              a new computational model for end-user development of data-centric web applications*,
              Proceedings of the 2016 ACM International Symposium on New Ideas, New Paradigms,
              and Reflections on Programming and Software, 2006.
.. [MODE2017] *MODELOFF - Financial Modeling World Championships*,
              http://www.modeloff.com/the-legend/.
.. [PERE2015] Perez, Fernando and Branger, Brian.
              *Project Jupyter: Computational Narratives as the
              Engine of Collaborative Data Science*, http://archive.ipython.org/JupyterGrantNarrative-2015.pdf.
.. [PYSPREAD] Manns, M. *PYSPREAD*, http://github.com/manns/pyspread.
.. [SCISHEET] *SciSheets*, https://github.com/ScienceStacks/SciSheets.
.. [STENCILA] *STENCILA*, https://stenci.la/.
.. [THIB2013] Thibodeau, Patrick.
              *India to overtake U.S. on number of developers by 2017*,
              COMPUTERWORLD, Jul 10, 2013.
