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
  var ep, scisheet, formula;
  scisheet = this.scisheet;
  ep = new SciSheetsUtilEvent(scisheet, oArgs);
  $(ep.target).effect("highlight", 1000000);
  $(ep.target).toggle("highlight");
  if (ep.columnName  === ROW_NAME) {
    scisheet.utilClick("NameColumnClickMenu", oArgs.event, function (eleId) {
      var msg;
      msg = "Row Name Column clicked.";
      console.log(msg);
      $(ep.target).stop();
    });
  } else {
    scisheet.utilClick("ColumnClickMenu", oArgs.event, function (eleId) {
      var msg, cmd, newPrompt;
      msg = "Column " + ep.columnName + " clicked.";
      msg += " Selected " + eleId + ".";
      console.log(msg);
      cmd = scisheet.createServerCommand();
      cmd.command = eleId;
      cmd.columnName = ep.columnName;
      cmd.target = "Column";
      if (cmd.command === 'Append') {
        scisheet.utilPromptForInput(cmd, "New column name", "");
      }
      if (cmd.command === 'Delete') {
        scisheet.utilSendAndReload(cmd);
      }
      if (cmd.command === 'Formula') {
        formula = scisheet.formulas[ep.columnName];
        scisheet.utilUpdateFormula(cmd, ep.columnName,
            formula, 1, oArgs);
      }
      if (cmd.command === 'Insert') {
        scisheet.utilPromptForInput(cmd, "New column name", "");
      }
      if (cmd.command === 'Move') {
        scisheet.utilPromptForInput(cmd, "Insert after column", "");
      }
      if (cmd.command === 'Refactor') {
        // Change the dialog prompt
        newPrompt = "Refactor column '" + ep.columnName + "': ";
        scisheet.utilPromptForInput(cmd, newPrompt, ep.columnName);
      }
      if (cmd.command === 'Rename') {
        // Change the dialog prompt
        newPrompt = "Rename column '" + ep.columnLabel + "': ";
        scisheet.utilPromptForInput(cmd, newPrompt, ep.columnLabel);
      }
    });
  }
};
