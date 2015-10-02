/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheetsUtilEvent, SciSheets, $, alert, YAHOO */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

function SciSheetsCell(scisheet) {
  "use strict";
  this.scisheet = scisheet;
}

SciSheetsCell.prototype.click = function (oArgs) {
  "use strict";
  var ep, msg;
  ep = new SciSheetsUtilEvent(this.scisheet, oArgs);
  msg = "Clicked cell = (" + ep.rowIndex + ", " + ep.columnIndex + ").";
  console.log(msg);
  this.scisheet.dataTable.onEventShowCellEditor(oArgs);
};

SciSheetsCell.prototype.modify = function (oArgs) {
  "use strict";
  var ep, msg;
  ep = new SciSheetsUtilEvent(this.scisheet, oArgs);
  msg = "Modified cell = (" + ep.rowIndex + ", " + ep.columnIndex + ").";
  console(msg);
};
