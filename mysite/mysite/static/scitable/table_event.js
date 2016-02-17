/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheets, $, alert, YAHOO */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */
/*jslint newcap: true */

function SciSheetsTable(scisheet) {
  "use strict";
  this.scisheet = scisheet;
}

SciSheetsTable.prototype.utilExportDialog = function (cmd) {
  // Inputs: cmd - command to process
  "use strict";
  var scisheet = this.scisheet;
  if (scisheet.mockAjax) {
    scisheet.ajaxCallCount += 1;  // Count as an Ajax call
  }
  $("#export-dialog").dialog({
    autoOpen: true,
    modal: true,
    closeOnEscape: false,
    dialogClass: "dlg-no-close",
    buttons: {
      "Submit": function () {
        cmd.args = [$("#export-dialog-function-name").val()];
        cmd.args.push($("#export-dialog-inputs").val());
        cmd.args.push($("#export-dialog-outputs").val());
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
};

SciSheetsTable.prototype.click = function (oArgs) {
  "use strict";
  var scisheet, scisheetTable;
  scisheetTable = this;
  scisheet = this.scisheet;
  this.scisheet.utilClick("TableClickMenu", function (eleId) {
    var cmd;
    console.log("Table click. Selected " + eleId + ".");
    cmd = scisheet.createServerCommand();
    cmd.command = eleId;
    cmd.target = "Table";
    if (cmd.command === 'Export') {
      scisheetTable.utilExportDialog(cmd);
    }
    if (cmd.command === 'Trim') {
      scisheet.utilSendAndReload(cmd);
    }
  });
};
