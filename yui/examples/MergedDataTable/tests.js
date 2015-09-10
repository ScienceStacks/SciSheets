/* Tests for Interactive Tables. */

/*jslint indent: 2 */
/*jslint browser: true*/
/*jslint unparam: true*/
/*global $, jQuery, alert, QUnit, createElementData */
/*jshint onevar: false */

QUnit.test("createElementData", function (assert) {
  "use strict";
  var tableElements = createElementData("cellediting");
  assert.ok(tableElements.table !== null,
      "table != null");
  assert.ok(tableElements.header.tagName === 'THEAD',
      "header.tagName == THEAD");
  assert.ok(tableElements.columns.length === 4,
      "columns.length == 4");
  assert.ok(tableElements.columns[0].element.innerHTML === "row",
      "columns[0] == 'row'");
});
