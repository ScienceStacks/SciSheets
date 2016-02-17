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
SciSheetsColumn.prototype.formula = function (cmd, formula) {
  // Change the dialog prompt
  "use strict";
  var scisheet, eleTextarea;
  scisheet = this.scisheet;
  eleTextarea = $("#formula-textarea")[0];
  if (formula != "") {
    eleTextarea.value = formula;
  }
  if (scisheet.mockAjax) {
    scisheet.ajaxCallCount += 1;  // Count as an Ajax call
  }
  $("#formula-dialog").dialog({
    autoOpen: true,
    modal: true,
    closeOnEscape: false,
    dialogClass: "dlg-no-close",
    buttons: {
      "Submit": function () {
        cmd.args = [eleTextarea.value];
        $(this).dialog("close");
        scisheet.utilSendAndReload(cmd);
      },
      "Cancel": function () {
        $(this).dialog("close");
        scisheet.utilReload();
      }
    }
  });
};

SciSheetsColumn.prototype.click = function (oArgs) {
  "use strict";
  var ep, scisheet, scisheetColumn, formula;
  scisheet = this.scisheet;
  scisheetColumn = this;
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
        scisheet.utilRename(cmd, "New column name", "");
      }
      if (cmd.command === 'Delete') {
        scisheet.utilSendAndReload(cmd);
      }
      if (cmd.command === 'Formula') {
        formula = scisheet.formulas[ep.columnName];
        scisheetColumn.formula(cmd, formula);
      }
      if (cmd.command === 'Insert') {
        scisheet.utilRename(cmd, "New column name", "");
      }
      if (cmd.command === 'Move') {
        scisheet.utilRename(cmd, "Insert after column", "");
      }
      if (cmd.command === 'Rename') {
        // Change the dialog prompt
        newPrompt = "Rename column '" + ep.columnName + "': ";
        scisheet.utilRename(cmd, newPrompt, "");
      }
    });
  }
};
