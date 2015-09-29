/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheets, SciSheetsUtilEvent, $, alert, YAHOO, SciSheetsUtilEvent */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

function SciSheetsRow(scisheet) {
  "use strict";
  this.scisheet = scisheet;
}

SciSheetsRow.prototype.click = function (oArgs) {
  "use strict";
  var ep;
  ep = new SciSheetsUtilEvent(this.scisheet, oArgs);
  SciSheetsUtilClick("RowClickMenu", function (eleId) {
    var msg;
    msg = "Row '" + ep.rowIndex + "' clicked.";
    msg += "Selected " + eleId;
    alert(msg);
  });
};
