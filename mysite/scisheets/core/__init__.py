'''
   This module provides a representation of tables that consist
   of equal length columns where all values in the column have
   the same data type.

   The core concepts are:
     A Cell is one data value in the table.
     A Column consists of ordered Cells of the same data type. 
       A Column Name is string that identifies the Column.
     A Column index is the 0-based offset of the Column
       within the Table.
     A ColumnContainer is a collection of Columns in which each
       each Column appears in a particular order.
     A Table is a ColumnContainer in which Columns have
       the same length and Column Names are unique.
     A Row is a collection of Cells from different Columns in a Table 
       at the same offset within their Column.
     The Row Index of a Row is the 0-based offset within each 
       Column of the Cells in the Row.
     A Row Name is a string that uniquely identifies the Row. This
       is the 1-based offset of the row in the Table.
     The Name Column is a Column in the Table that contains the
       Row Names. It is at Column Index 0, and has the name "row".
       The Name Column is created automatically when the Table is
       created, and is maintained automatically.

  The use cases supported are:
    1. Create a new Table.
    2. Create a Column and add it to a Table.
    3. Add a Row to a Table.
    4. Update the values of one or more Cells in a Row.
    5. Delete a Row, Column, or Table.
    6. Insert a Row between existing Rows.
    7. Make a copy of a Row, Column, or Table.

  In support of these use cases, the following operations can be
  performed on Tables, Rows and Columns.
    1. Create
    2. Copy
    3. Delete
  In addition, 
    1. Insert a Row or Column into a Table at a particular index.
    2. Update one or more Cells in a Row.
'''
