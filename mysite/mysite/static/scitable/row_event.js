/*jslint newcap: true */
/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheets, $, alert, YAHOO, SciSheetsUtilEvent */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

function SciSheetsRow(scisheet) {
  "use strict";
  this.scisheet = scisheet;
}

SciSheetsRow.prototype.click = function (oArgs) {
  "use strict";
  var ep, scisheet;
  scisheet = this.scisheet;
  ep = new SciSheetsUtilEvent(this.scisheet, oArgs);
  $(ep.target).effect("highlight", 1000000);
  $(ep.target).toggle("highlight");
  scisheet.utilClick("RowClickMenu", function (eleId) {
    var msg, cmd, ele;
    msg = "Row '" + ep.rowIndex + "' clicked.";
    msg += " Selected " + eleId + ".";
    console.log(msg);
    cmd = scisheet.createServerCommand();
    cmd.command = eleId;
    cmd.row = ep.rowIndex;
    cmd.target = "Row";
    if (cmd.command === 'Insert') {
      scisheet.utilSendAndReload(cmd);
    }
    if (cmd.command === 'Append') {
      scisheet.utilSendAndReload(cmd);
    }
    if (cmd.command === 'Rename') {
      // Change the dialog prompt
      ele = $("#rename-dialog-label")[0].childNodes[0];
      ele.nodeValue = "Rename row '" + ep.rowIndex + "': ";
      if (scisheet.mockAjax) {
        scisheet.ajaxCallCount += 1;  // Count as an Ajax call
      }
      $("#rename-dialog").dialog({
        autoOpen: true,
        modal: true,
        closeOnEscape: false,
        dialogClass: "dlg-no-close",
        buttons: {
          "Submit": function () {
            cmd.args = [$("#rename-dialog-name").val()];
            $(this).dialog("close");
            scisheet.utilSendAndReload(cmd);
            alert("Pressed Submit");
          },
          "Cancel": function () {
            $(this).dialog("close");
            scisheet.utilReload();
          }
        }
      });
    }
    if (cmd.command === 'Delete') {
      scisheet.utilSendAndReload(cmd);
    }
  });
};


