# SciSheets
SciSheets is a project that is re-thinking the use of spreadsheets for scientists.

Spreadsheets are widely used by scientists to do data analysis. There are several reasons for this. One is the wide spread availability of inexpensive spreadsheet systems such as OpenOffice and Google Sheets as well as Microsoft Excel. A second is that spreadsheets provide a conceptually simple way to do calculations that avoids the mental burdens of programming, especially for control flow and concerns related to data types.

However, today's spreadsheet systems have many shortcomings.
In particular, spreadsheets suffer from:
- poor scalability because executing formulas within the spreadsheet system has high overhead; 
- great difficulty with reuse because there is no concept of encasulation (and even different
length data are problematic);
- great difficulty with transitioning from a spreadsheet to a program to facilitate integration into software systems and improve
scalability;
- limited ability to handle complex data because there is no concept of structured data;
- poor readability because formulas must be expressions (not scripts) and any cell may have a formula; and
- limited ability to express calculations because formulas are limited to using a few hundred or so functions provided by the spreadsheet system.

SciSheets addresses these shortcomings with several features. 
SciSheets provides:
- formulas that are Python expressions or scripts to improve expressiveness and access to complex computations in Python packages;
- export spreadsheets as standalone Python programs thereby providing scalability and reuse of calculations in formulas and software; and
- hierarhical tables and cells that may have multiple values to handle complex data such as n-to-m relationships.

SciSheets is a web application that is accessed from a web browser. So, no program installation is required to use SciSheets. A beta release of SciSheets is planned for the end of 2016. Currently, SciSheets is at an alpha level that is suitable for evaluation purposes. Please contact jlheller@uw.edu if you are interested in doing such an evaluation.

More details can be found in the [SciSheets summary] (https://docs.google.com/document/d/1dOgMzlOWAx5SGB8ev_E02jO79eewbPZ25m37SrK7IAo/edit#heading=h.lmbccclro00t).

The following is for interested developers. SciSheets makes use of a related project, BaseStack, that provides an easy way to install web applications in VMs.

To install on a virgin VM:

1. Copy ScienceStacks/BaseStack/setup.sh to $HOME

2. bash setup_vm.sh

3. Answer "yes" as required and enter root password

4. cd $HOME

5. git clone --recursive https://github.com/ScienceStacks/SciSheets.git

6. cd SciSheets

7. bash setup.sh

Note that you will also need to install pandas if you want to make use of its python packages.
