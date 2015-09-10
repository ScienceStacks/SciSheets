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
  Utility routines used for table codes.
*/

// Constructs the table element data
// Input: tableId - ID of the table
// Output: JSON structure with
//  table: element where table begins
//  theader: header element
//  columns:
//    name: column name
//    element: element object
//  tdata: tdata element
//  cells:
//    column: column name
//    row: row number
//    element: element object
function createElementData(tableId) {
  "use strict";
  var c, r, spans, elements, element, name, tdataRows, rowData, cell,
    tableElements = {"table": null,
                     "theader": null,
                     "columns": [],
                     "tdata": null,
                     "cells": []
                    };
  tableElements.table = document.getElementById(tableId);
  tableElements.theader = tableElements.table.getElementsByTagName('thead')[0];
  elements = tableElements.theader.getElementsByTagName('th');
  for (c = 0; c < elements.length; c++) {
    spans = elements[c].getElementsByTagName('span');
    element = spans[0];
    name = element.innerHTML;
    tableElements.columns.push({"name": name, "element": element});
  }
  tableElements.tdata = $('.yui-dt-data')[0];
  tdataRows = tableElements.tdata.getElementsByTagName('tr');
  for (r = 0; r < tdataRows.length; r++) {
    rowData = tdataRows[r].getElementsByTagName('td');
    for (c = 0; c < tableElements.columns.length; c++) {
      element = rowData[c];
      cell = {"column": tableElements.columns[c].name,
              "row": c + 1,
              "element": element
             };
      tableElements.cells.push(cell);
    }
  }
  return tableElements;
}
