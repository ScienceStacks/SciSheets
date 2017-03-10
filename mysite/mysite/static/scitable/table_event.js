/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheets, $, alert, YAHOO, SciSheetsUtilEvent, SciSheetsColumn */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */
/*jslint newcap: true */

function SciSheetsTable(scisheet) {
  "use strict";
  this.scisheet = scisheet;
}

SciSheetsTable.prototype.click = function (oArgs) {
  "use strict";
  var ep, scisheet, scisheetTable, scisheetColumn, processClick;
  scisheetTable = this;
  scisheet = scisheetTable.scisheet;

  processClick = function (eleId) {
    /* Processes a click on a Table menu */
    /* Input: eleId - menu item selection */
    scisheet.utilMenuProcessor(eleId, oArgs, "Table");
  };

  ep = new SciSheetsUtilEvent(scisheet, oArgs);
  $(ep.target).effect("highlight", 1000000);
  $(ep.target).toggle("highlight");
  if (scisheet.responseSchema.indexOf(ep.columnName) > -1) {
    /* Check if this is a Column instead of a Table */
    scisheetColumn = new SciSheetsColumn(scisheet);
    scisheetColumn.click(oArgs);
  } else {
    /* Is a table command. */
    scisheet.utilClick("TableClickMenu", oArgs, processClick);
  }
};
