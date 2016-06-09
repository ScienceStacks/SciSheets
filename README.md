# SciSheets
SciSheets is a project that is re-thinking the use of spreadsheets for scientists.

Spreadsheets are widely used by scientists to do data analysis. There are several reasons for this. One is the wide spread availability of inexpensive spreadsheet systems such as OpenOffice and Google Sheets as well as Microsoft Excel. A second is that spreadsheets provide a conceptually simple way to do calculations that avoids the mental burdens of programming, especially for control flow and concerns related to data types.

However, today's spreadsheet systems have many shortcomings. First, spreadsheets suffer from poor readability. That is, it's very difficult to read a spreadsheet formula and understand the calculation being performed, unless it's a very simple formula. Also, spreadsheets scale poorly as they grow in size because executing formulas within the spreadsheet system has high overhead. Further, spreadsheet users often find it difficult to express their calculations because formulas are limited to using a few hundred or so functions provided by the spreadsheet system. Last, spreadsheets are notriously difficult to reuse, other than by copy and paste into another spreadsheet.

SciSheets addresses these shortcomings with several features. First, SciSheets formulas apply to an entire column, not just a single cell. This improves readability by limiting the number of formulas in a spreadsheet and providing a more natural expression of the formulas. Second, SciSheets formulas are python expressions and statements. This improves expressiveness by giving users access to many thousands of python packages (e.g., for machine learning, text analytics, and symboic mathematics) as well as the ability to express calculations algorithmically in scripts. Last, SciSheets tables can be exported as standalone python programs. This improves scalability since formulas execute in python, instead of the spreadsheet system. Exporting spreadsheets to python also provides for reuse since the exported program can be used in a SciSheets formula.

SciSheets is a web application that is accessed from a web browser. So, no program installation is required to use SciSheets. A beta release of SciSheets is planned for the end of 2016. Currently, SciSheets is at an alpha level that is suitable for evaluation purposes. Please contact jlheller@uw.edu if you are interested in doing such an evaluation.

More details can be found in the [SciSheets overview document] (https://docs.google.com/document/d/1dOgMzlOWAx5SGB8ev_E02jO79eewbPZ25m37SrK7IAo/edit#heading=h.lmbccclro00t).

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
