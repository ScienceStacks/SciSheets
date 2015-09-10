// TODO: Finish debugging. Add accessor methods
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


/* ---------------- Internal Classes ----------------*/
function TableRow(row, element) {
  "use strict";
  this.row = row;
  this.element = element;
}

function TableColumn(column, element) {
  "use strict";
  this.column = column;
  this.element = element;
}

function TableCell(row, column, element) {
  "use strict";
  this.row = row;
  this.column = column;
  this.element = element;
}

/*------------ External Class -----------*/

function TableElements(tableName) {
  "use strict";
  this.tableName = tableName;
  this.tableElement = document.getElementById(this.tableName);
  this.columns = [];  // Array of TableColumn
  this.rows = [];  // Array of TableRow
  this.cells = [];  // Array of TableCell
}

TableElements.prototype.init = function () {
  "use strict";
  this.initColumns();
  this.initCells();
  this.initRows();
};

TableElements.prototype.initColumns = function () {
  "use strict";
  var c, elements, theader, spans, name, element, col;
  theader = this.table.getElementsByTagName('thead')[0];
  elements = theader.getElementsByTagName('th');
  for (c = 0; c < elements.length; c++) {
    spans = elements[c].getElementsByTagName('span');
    element = spans[0];
    name = element.innerHTML;
    col = new TableColumn(name, element);
    this.columns.push(col);
  }
};

TableElements.prototype.initCells = function () {
  "use strict";
  var tdata, r, c, cell, rows, row;
  tdata = $('.yui-dt-data')[0];
  rows = tdata.getElementsByTagName('tr');
  for (r = 0; r < rows.length; r++) {
    row = rows[r].getElementsByTagName('td');
    for (c = 0; c < this.columns.length; c++) {
      cell = new TableCell(r + 1, this.columns[c], row[c]);
      this.Cells.push(cell);
    }
  }
};

TableElements.prototype.initRows = function () {
  "use strict";
  var i, cell, row;
  for (i = 0; i < this.cells.length; i++) {
    cell = this.cells[i];
    if (cell.column === 'row') {
      row = new TableRow(cell.row, cell.element);
      this.rows.push(row);
    }
  }
};
