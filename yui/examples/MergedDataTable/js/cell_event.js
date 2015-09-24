/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheets, $, alert, YAHOO */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

SciSheets.prototype.cell_click = function (ep, oArgs) {
  "use strict";
  var msg;
  msg = "Clicked (r,c) = (" + ep.rowIndex + ", " + ep.columnIndex + ")";
  alert(msg);
  this.dataTable.onEventShowCellEditor(oArgs);
};
