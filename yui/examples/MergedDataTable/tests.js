/* Tests for Interactive Tables. */

/*jslint indent: 2 */
/*jslint browser: true*/
/*jslint unparam: true*/
/*global $, jQuery, alert, QUnit, TableElements */
/*jshint onevar: false */

QUnit.test("createElementData", function (assert) {
  "use strict";
  var tableElements = new TableElements("cellediting");
  assert.ok(tableElements.table !== null,
      "table != null");
  assert.ok(tableElements.columns.length === 4,
      "columns.length == 4");
  assert.ok(tableElements.cells.length === 20,
      "cells.length == 20");
  assert.ok(tableElements.columns[0].element.innerHTML === "row",
      "columns[0] == 'row'");
});
