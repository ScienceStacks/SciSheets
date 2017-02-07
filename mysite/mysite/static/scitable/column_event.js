/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheetsUtilEvent, $, alert, YAHOO */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */
/*jslint newcap: true */

function SciSheetsColumn(scisheet) {
  "use strict";
  this.scisheet = scisheet;
}

SciSheetsColumn.prototype.click = function (oArgs) {
  "use strict";
  var ep, scisheet, processClick, scisheetColumn;
  scisheetColumn = this;
  scisheet = scisheetColumn.scisheet;

  processClick = function (eleId) {
    scisheet.utilMenuProcessor(eleId, oArgs, "Column");
  };

  ep = new SciSheetsUtilEvent(scisheet, oArgs);
  if (ep.columnLabel  === scisheet.ROWNAME) {
    scisheet.utilClick("NameColumnClickMenu", oArgs, function (eleId, oArgs) {
      var msg;
      msg = "Row Name Column clicked: " + ep.columnName;
      console.log(msg);
      $(ep.target).stop();
    });
  } else {
    scisheet.utilClick("ColumnClickMenu", oArgs, processClick);
  }
};
