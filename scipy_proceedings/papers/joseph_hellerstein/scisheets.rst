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

Introduction
------------

Digital spreadsheets are the "killer app" that ushered in the PC revolution. 
This is largely because spreadsheets provide a conceptually simple way to do calculations that avoids the mental burdens of programming, 
especially considerations of control flow, data dependencies, and data structures. 
Recent estimates suggest that over 800M professionals author spreadsheet formulas as part of their work
ref?? http://www.modeloff.com/the-legend/), which is about 50 times the number
of software developers world wide
ref?? (http://www.computerworld.com/article/2483690/it-careers/india-to-overtake-u-s--on-number-of-developers-by-2017.html).

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
However, many innovative spreadsheet systems have introduced.
Google Fusion Tables ref?? uses column formulas to avoid a common source of errors,
the need to copy formulas as rows are added/deleted from a table.
The Pyspread ref?? project uses Python as the formula language, which increases the expressiveness of formulas.
A more radical approach is taken by
the Stencila system ref??, which
provides a document structure that includes cells that execute formulas, including the display of of data tables;
cells may execute statements from many languages including Python and R.

Sadly, even with the aforementioned innovations in spreadsheets, 
serious deficiencies remain.

1. The expressiveness of formulas is limited because formulas are restricted to being expressions, not scripts (although Stencila does provide a limited form of scripting).
2. None of the innovations eases the burden of 
   dealing with complex data relationships, such as n-to-m relationships.
3. None of the innovations address code sharing and reuse between 
   spreadsheet users or between spreadsheet users and software engineers.
4. Very little has been done to address the performance problems that occur as spreadsheets scale.

This paper introduces SciSheets ref?? githubURL, a new spreadsheet system with the goal of delivering
the power of programming with the simplicity of spreadsheets. 
Our target users are technical professionals, such as scientists and finanical engineers,
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

Motivating Examples and Use Cases
---------------------------------

SciSheets Design
----------------

User Experiences
----------------

- Screenshots

Future Work
-----------

- Local scopes in hierarchial tables and the implications for copy

- Graphics

- Replay log

- Multiple languages (R)


References
----------
.. [Atr03] P. Atreides. *How to catch a sandworm*,
           Transactions on Terraforming, 21(3):261-300, August 2003.


