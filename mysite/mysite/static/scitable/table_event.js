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

SciSheetsTable.prototype.utilSelectFile = function (fileNames) {
  // Inputs: fileNames - array of file names to select
  "use strict";
  var options, n, ele, name, selMenu, scisheet, cmd, selFunction;
  // List of selection options
  selMenu = $("#select-file");
  selFunction = function () {
    cmd = scisheet.createServerCommand();
    cmd.target = "Table";
    cmd.args = [this.id];
    cmd.command = "OpenTableFile";
    $(selMenu).css("display", "none");
    scisheet.utilSendAndReload(cmd);
  };
  scisheet = this.scisheet;
  // Function performed on the user selection
  // Set the id of each option to the file name
  options = "";
  for (n = 0; n <  fileNames.length; n++) {
    name = fileNames[n];
    options = options + "<option id='" + name + "'>"
              + name + "</option>";
  }
  $(selMenu).append(options);
  for (n = 0; n < fileNames.length; n++) {
    ele = "#" + fileNames[n];
    $(ele).click(selFunction);
  }
  //$(selMenu).css("display", "block");
  //$(selMenu).find('select').selectmenu('refresh');
  $(selMenu).dialog({
    autoOpen: true,
    modal: true,
    closeOnEscape: true,
    dialogClass: "dlg-no-close",
    close: function (event, ui) {
      scisheet.utilReload();
    }
  });
  $(selMenu).dialog("option", "width", 50);
  $(selMenu).dialog("option", "height", 80);
  $(selMenu).parent().find(".ui-dialog-titlebar").hide();
};

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
    closeOnEscape: true,
    close: function (event, ui) {
      scisheet.utilReload();
    },
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
    if (cmd.command === 'Delete') {
      scisheet.utilSendAndReload(cmd);
    }
    if (cmd.command === 'Export') {
      scisheetTable.utilExportDialog(cmd);
    }
    if (cmd.command === 'New') {
      scisheet.utilSendAndReload(cmd);
    }
    if (cmd.command === 'Open') {
      cmd.command = 'ListTableFiles';
      scisheet.sendServerCommand(cmd, function (names) {
        // User selects the file to open
        scisheetTable.utilSelectFile(names);
      });
    }
    if (cmd.command === 'Rename') {
      scisheet.utilRename(cmd, "New table name", "");
    }
    if (cmd.command === 'SaveAs') {
      scisheet.utilRename(cmd, "Table file name", scisheet.tableFile);
    }
    if (cmd.command === 'Trim') {
      scisheet.utilSendAndReload(cmd);
    }
  });
};
