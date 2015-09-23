/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, SciSheets */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

// Data and column setup
SciSheets.prototype.util.formatColumn = function (name) {
  "use strict";
  var localName = name;
  return function (elCell, oRecord, oColumn, oData) {
    elCell.innerHTML = "<pre class=\"" + localName + "\">" + YAHOO.lang.escapeHTML(oData) + "</pre>";
  };
};

// EventProcessing Object
SciSheets.prototype.util.eventProcessing = function (table, oArgs) {
  "use strict";
  // var target, columnName, columnIndex, rowIndex;
  this.target = oArgs.target;
  this.columnName = table.getColumn(this.target).field;
  this.columnIndex = table.getCellIndex(this.target) + 1;
  this.rowIndex = table.getRecordIndex(this.target) + 1;
};
