/*jslint indent: 2 */
/*jslint browser: true*/
/*jslint unparam: true*/
/*global $, alert, YAHOO */
/*jshint onevar: false */
/*jslint plusplus: true */
/*jshint yui: true */
/*jshint jquery: true */
/*jshint qunit: true */

/*
   What's next:
     Finish debugging. Add accessor methods
*/

/*
  Creates a class that contains the table elements
  that consists of the table, columns, rows, and cells.

// Constructs the table element data
// Input: tableId - ID of the table
// Output: JSON structure with
//  table: element where table begins
//  columns:
//    name: column name
//    element: element object
//  tdata: tdata element
//  cells:
//    column: column name
//    row: row number
//    element: element object
*/

/********** TableRow **************/
function TableRow(name, element) {
  "use strict";
  this.name = name;
  this.element = element;
}

/********** TableColumn **************/
function TableColumn(name, element) {
  "use strict";
  this.name = name;
  this.element = element;
}

/********** TableCells **************/
function TableCell(rowName, columnName, element) {
  "use strict";
  this.rowName = rowName;
  this.columnName = columnName;
  this.element = element;
}


/***************************************/
/********** TableElements **************/
/***************************************/
function TableElements(tableName) {
  "use strict";
  this.tableName = tableName;
  this.tableElement = document.getElementById(this.tableName);
  this.columns = [];  // Array of TableColumn
  this.rows = [];  // Array of TableRow
  this.cells = [];  // Array of TableCell
  this.zInit();  // Fill in columns, rows, cells
}

TableElements.prototype.GetTableRow = function (element) {
  "use strict";
  var elements;
  elements = this.zFindElements(this.rows, element);
  if (elements.length !== 1) {
    console.log("**Error. Found " + elements.length + "!= 1");
    elements = null;  // Ensure get an error on return
  }
  return elements[0];
};

// ----------- INTERNAL METHODS

TableElements.prototype.zInit = function () {
  "use strict";
  this.zInitColumns();
  this.zInitCells();
  this.zInitRows();
};

TableElements.prototype.zInitCells = function () {
  "use strict";
  var tdata, r, c, cell, rows, row;
  tdata = $('.yui-dt-data')[0];
  rows = tdata.getElementsByTagName('tr');
  for (r = 0; r < rows.length; r++) {
    row = rows[r].getElementsByTagName('td');
    for (c = 0; c < this.columns.length; c++) {
      cell = new TableCell(r + 1, this.columns[c].name, row[c]);
      this.cells.push(cell);
    }
  }
};

TableElements.prototype.zInitColumns = function () {
  "use strict";
  var c, elements, theader, spans, name, element, col;
  theader = this.tableElement.getElementsByTagName('thead')[0];
  elements = theader.getElementsByTagName('th');
  for (c = 0; c < elements.length; c++) {
    spans = elements[c].getElementsByTagName('span');
    element = spans[0];
    name = element.innerHTML;
    col = new TableColumn(name, element);
    this.columns.push(col);
  }
};

TableElements.prototype.zInitRows = function () {
  "use strict";
  var i, cell, row;
  for (i = 0; i < this.cells.length; i++) {
    cell = this.cells[i];
    if (cell.columnName === 'row') {
      row = new TableRow(cell.rowName, cell.element);
      this.rows.push(row);
    }
  }
};

// Finds the matching element in an array of objects that have
// the element property.
// Input: theArray - an array of objects that
//                   has an element property
//        theElement - the element to locate
// Output: result - the object with a matching element
// Output: anE
TableElements.prototype.zFindElements = function (theArray, theElement) {
  "use strict";
  var result;
  result = [];
  theArray.forEach(function (entry) {
    if (entry.element === theElement) {
      result.push(entry);
    }
  });
  return result;
};

