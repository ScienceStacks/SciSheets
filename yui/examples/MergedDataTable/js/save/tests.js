/* Tests for Interactive Tables. */

/*jslint indent: 2 */
/*jslint browser: true*/
/*jslint unparam: true*/
/*global $, jQuery, alert, QUnit, TableElements, TableRow, TableColumn */
/*jshint onevar: false */

QUnit.test("createElementData", function (assert) {
  "use strict";
  var tableElements, rows_x, rows, cols, cols_x, sTableRow, rTableRow;
  tableElements = new TableElements("cellediting");
  assert.ok(tableElements.table !== null,
      "table != null");
  assert.ok(tableElements.columns.length === 4,
      "columns.length == 4");
  assert.ok(tableElements.cells.length === 20,
      "cells.length == 20");
  assert.ok(tableElements.rows.length === 5,
      "rows.length == 5");
  assert.ok(tableElements.columns[0].element.innerHTML === "row",
      "columns[0] == 'row'");

  rows = [new TableRow(1, "x"), new TableRow(2, "y"), new TableRow(3, "x")];
  rows_x = tableElements.zFindElements(rows, "x");
  assert.ok(rows_x.length === 2, "zFindElements");

  cols = [new TableColumn(1, "x"), new TableColumn(2, "y"), new TableColumn(3, "x")];
  cols_x = tableElements.zFindElements(cols, "x");
  assert.ok(cols_x.length === 2, "zFindElements");

  sTableRow = tableElements.rows[0];
  rTableRow = tableElements.GetTableRow(sTableRow.element);
  assert.ok(sTableRow === rTableRow, "GetTableRow");
});
