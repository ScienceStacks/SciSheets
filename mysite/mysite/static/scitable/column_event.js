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
      var msg, cmd, ele;
      msg = "Column " + ep.columnIndex + " (" + ep.columnName + ")" + " clicked.";
      msg += " Selected " + eleId + ".";
      console.log(msg);
      cmd = scisheet.createServerCommand();
      cmd.command = eleId;
      cmd.column = ep.columnIndex;
      cmd.target = "Column";
      // $("#rename-dialog").css("display", "block");
      if (cmd.command === 'Rename') {
        // Change the dialog prompt
        ele = $("#rename-dialog-label")[0].childNodes[0];
        ele.nodeValue = "Rename column '" + ep.columnName + "': ";
        $("#rename-dialog").dialog({
          autoOpen: true,
          modal: true,
          dialogClass: "dlg-no-close",
          buttons: {
            "Submit": function () {
              cmd.args = [$("#rename-dialog-name").val()];
              $(this).dialog("close");
              scisheet.utilSendAndReload(cmd);
            },
            "Cancel": function () {
              $(this).dialog("close");
            }
          }
        });
      }
      if (cmd.command === 'Delete') {
        scisheet.utilSendAndReload(cmd);
      }
    });
  }
};
