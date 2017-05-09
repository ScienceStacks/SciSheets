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

Digital spreadsheets are the "killer app" that ushered in the PC revolution. This is largely because spreadsheets provide a conceptually simple way to do calculations that avoids the mental burdens of programming, especially considerations of control flow, data dependencies, and data structures. Spreadsheets are likely the most popular computational environment on the planet (Scaffidi et al., IEEE Symposium on Visual Languages and Human-Centric Computing, 2005).

However, today's spreadsheet systems have many shortcomings. In particular, spreadsheets suffer from:
   
- poor scalability because executing formulas within the spreadsheet system has high overhead;
- great difficulty with reuse because there is no concept of encapsulation (and even different length data are problematic);
- great difficulty with transitioning from a spreadsheet to a program to facilitate integration into software systems and improve scalability;
- limited ability to handle complex data because there is no concept of structured data;
- poor readability because formulas must be expressions (not scripts) and any cell may have a formula; and
- limited ability to express calculations because formulas are limited to using a few hundred or so functions provided by the spreadsheet system (or specially coded macros).

This paper introduces SciSheets, a new spreadsheet system that is intended to
to deliver the power of programming with the simplicity of spreadsheets. To date, our focus has been on a simple environment
for spreadsheet users to do calculations not the many other features of spreadsheets such as formating and plotting (although we
discuss our plans for handling graphics in the future work setting).
The core features of SciSheets are:

(i) formulas that are Python expressions or scripts to improve
expressiveness and provide access to complex computations in 
Python packages;
(b) exporting spreadsheets as standalone Python programs to improve 
scalability and enable reuse of spreadsheet calculations 
in other spreadsheets and in programs; and
(c) nested tables and cells that may have multiple 
values to handle complex data such as n-to-m relationships.

Issues associated with spreadsheet programming have been largely ignored in the computer science academic literature.
However, there have been other spreadhseet systems introduced that address some of issues considered by SciSheets.
Systems such as Mathematica ref?? and SPSS ref?? provide a grid view of data, but not spreadsheet formulats
or automated recalculations as is expected by spreadsheet users.
SciSheets use of column formulas is not unique (e.g.,
Google Fusion Tables ref??),
an approach that
eliminates the need to copy formulas as rows are added/deleted from a table.
However, unlike existing approaches to column formulas,
SciSheets formulas can be scripts, not just expressions.
This enhancement greatly extends the computation expressiveness of the spreadsheet, but it also creates challenges,
such as localizing programming errors to aid in debugging.
The Stencila ref? and Pyspread ref?? projects are spreadsheet systems that, like SciSheets, use python as the formula language. 
SciSheets differs from these projects in that SciSheets provides a way to structure complex data using column hierarchies.
Doing so has many benefits, including the ability to express n-to-m relationships (which is very
difficult in a simple table).
Last, SciSheets allows for the export of a spreadsheet as a standalone python program, a feature that we have not seen
in any existing system.
This features has numerous benefits, including: program reuse, scalability, and enhanced collaboration with software engineers.

Some notes

  - Separate world of spreadsheet users, including competitions for top proficiency (e.g., Modeloff http://www.modeloff.com/the-legend/). 
  - Estimate 800M professionals users of excel worldwide. (modeloff)
  - Estimate 18M profession software developers worldwide in 2017 (http://www.computerworld.com/article/2483690/it-careers/india-to-overtake-u-s--on-number-of-developers-by-2017.html)

- Appeal of spreadsheets for scientists

- Shortcomings of spreadsheets

  - London Whale error - http://www.businessinsider.com/excel-partly-to-blame-for-trading-loss-2013-2

- Scisheets principles

- Problem domain for evaluating scisheets


Biological Data and Use Cases
-----------------------------

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


