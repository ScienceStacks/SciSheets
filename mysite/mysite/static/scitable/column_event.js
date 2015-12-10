/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheetsUtilEvent, $, alert, YAHOO, SciSheetsUtilClick */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */
/*jslint newcap: true */

var ROW_NAME = "row";

function SciSheetsColumn(scisheet) {
  "use strict";
  this.scisheet = scisheet;
}

SciSheetsColumn.prototype.click = function (oArgs) {
  "use strict";
  var ep, scisheet;
  scisheet = this.scisheet;
  ep = new SciSheetsUtilEvent(scisheet, oArgs);
  if (ep.columnName  === ROW_NAME) {
    SciSheetsUtilClick("FirstColumnClickMenu", function (eleId) {
      var msg;
      msg = "Row Name Column clicked.";
      console.log(msg);
    });
  } else {
    SciSheetsUtilClick("ColumnClickMenu", function (eleId) {
      var msg, cmd;
      msg = "Column " + ep.columnIndex + " (" + ep.columnName + ")" + " clicked.";
      msg += " Selected " + eleId + ".";
      console.log(msg);
      cmd = scisheet.createServerCommand();
      cmd.command = eleId;
      cmd.column = ep.columnIndex;
      cmd.target = "Column";
      if (cmd.command === 'Rename') {
        cmd.args = ["new name"];
      }
      scisheet.sendServerCommand(cmd, function (data) {
        console.log("Server returned: " + data);
        window.location.href = 'http://localhost:8000/scisheets/';  // reload the page
      });
    });
  }
};
