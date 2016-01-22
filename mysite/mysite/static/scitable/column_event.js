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
  $(ep.target).effect("highlight", 1000000);
  $(ep.target).toggle("highlight");
  if (ep.columnName  === ROW_NAME) {
    scisheet.utilClick("NameColumnClickMenu", function (eleId) {
      var msg;
      msg = "Row Name Column clicked.";
      console.log(msg);
      $(ep.target).stop();
    });
  } else {
    scisheet.utilClick("ColumnClickMenu", function (eleId) {
      var msg, cmd, newPrompt;
      msg = "Column " + ep.columnIndex + " (" + ep.columnName + ")" + " clicked.";
      msg += " Selected " + eleId + ".";
      console.log(msg);
      cmd = scisheet.createServerCommand();
      cmd.command = eleId;
      cmd.column = ep.columnIndex;
      cmd.target = "Column";
      if (cmd.command === 'Append') {
        scisheet.utilRename(cmd, "New column name");
      }
      if (cmd.command === 'Delete') {
        scisheet.utilSendAndReload(cmd);
      }
      if (cmd.command === 'Insert') {
        scisheet.utilRename(cmd, "New column name");
      }
      if (cmd.command === 'Move') {
        scisheet.utilRename(cmd, "Insert after column");
      }
      if (cmd.command === 'Rename') {
        // Change the dialog prompt
        newPrompt = "Rename column '" + ep.columnName + "': ";
        scisheet.utilRename(cmd, newPrompt);
      }
    });
  }
};
