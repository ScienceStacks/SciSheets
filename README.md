# SciSheets
SciSheets is a project that is re-thinking the use of spreadsheets for scientists.

Spreadsheets are widely used by scientists to do data analysis. There are several reasons for this. One is the wide spread availability of inexpensive spreadsheet systems such as OpenOffice and Google Sheets as well as Microsoft Excel. A second is that spreadsheets provide a conceptually simple way to do calculations that avoids the mental burdens of programming, especially for control flow and data input and output.

However, spreadsheets are notorious for their limitations as well: poor scalability, limited ability to do code sharing and resuse, and extreme difficulty with documentation (since knowledge of every cell is required). The end result is that current spreadsheet systems lack the features (and restrictions) that make it so that scientists create scalable, reproducible, and reusable scientific analyses.

SciSheets is a new spreadsheet system for scientists. The guiding principle is to create a spreadsheet system in which scientists will do "the right thing" by default. For example, SciSheets does not have cell formulas, only column formulas. This greatly simplifies documentation. Other systems (e.g., Google Fusion Tables) implement column formulas in a way that greatly restricts the computations that can be done. The SciSheets implementation provides great flexibility by introducing the idea cell relative addressing for recurrence relationships to reference the previous and current cell in a column. Beyond this, SciSheets allows users to export their spreadsheets as python programs. Doing so provides considerable scalability for computations and data. Last, python programs can be used in spreadhseet formulas, thereby providing a way to share and reuse spreadsheet codes.

SciSheets is at a pre-alpha level. A 0.1 release is expected rearly in 2016.

The following is for interested developers. SciSheets makes use of a related project, BaseStack, that provides an easy way to install web applications in VMs.

To install on a virgin VM:

1. Copy ScienceStacks/BaseStack/setup.sh to $HOME

2. bash setup_vm.sh

3. Answer "yes" as required and enter root password

4. cd $HOME

5. git clone --recursive https://github.com/ScienceStacks/SciSheets.git

6. cd SciSheets

7. bash setup.sh
