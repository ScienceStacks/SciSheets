/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheets, SciSheetsTable, $, alert, YAHOO */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */
/*jslint newcap: true */

function SciSheetsSheet(scisheet) {
  "use strict";
  this.scisheet = scisheet;
  this.scisheetTable = new SciSheetsTable(scisheet);
}

SciSheetsSheet.prototype.utilSelectFile = function (fileNames) {
  // Inputs: fileNames - array of file names to select
  "use strict";
  var options, n, ele, name, selMenu, scisheet, cmd, selFunction;
  // List of selection options
  selMenu = $("#select-file");
  selFunction = function () {
    cmd = scisheet.createServerCommand();
    cmd.target = "Sheet";
    cmd.args = [this.id];
    cmd.command = "OpenSheetFile";
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
  $(selMenu).dialog({
    autoOpen: true,
    modal: true,
    closeOnEscape: true,
    dialogClass: "dlg-no-close",
    close: function (event, ui) {
      scisheet.utilReload();
    }
  });
  $(selMenu).dialog("option", "width", 80);
  $(selMenu).dialog("option", "height", 80);
  $(selMenu).parent().find(".ui-dialog-titlebar").hide();
};

SciSheetsSheet.prototype.utilExportDialog = function (cmd) {
  // Inputs: cmd - command to process
  "use strict";
  var scisheet = this.scisheet;
  if (scisheet.mockAjax) {
    scisheet.ajaxCallCount += 1; // Count as an Ajax call
  }
  $("#export-dialog").css("display", "block");
  $("#export-dialog").draggable();
  //leftPos = evObj.pageX1+30;
  //topPos = 10;
  //$("#export-dialog").css({left: leftPos, top: topPos});
  $(document).keydown(function (e) {
    if (e.keyCode === 27) {
      $("#export-dialog").css("display", "none");
    }
  });
  $("#export-dialog-submit").click(function () {
    cmd.args = [$("#export-dialog-function-name").val()];
    cmd.args.push($("#export-dialog-inputs").val());
    cmd.args.push($("#export-dialog-outputs").val());
    $("#export-dialog").css("display", "none");
    scisheet.utilSendAndReload(cmd);
  });
  $("#export-dialog-cancel").click(function () {
    $("#export-dialog").css("display", "none");
    scisheet.utilReload();
  });
};

SciSheetsSheet.prototype.click = function (oArgs) {
  "use strict";
  var scisheet, scisheetSheet, processClick;
  scisheetSheet = this;
  scisheet = scisheetSheet.scisheet;

  processClick = function (eleId) {
    var cmd, tableCommands, simpleCommands;
    console.log("Table click. Selected " + eleId + ".");
    cmd = scisheet.createServerCommand();
    cmd.command = eleId;
    tableCommands = ['Epilogue', 'Prologue', 'Rename', 'Trim', 'Unhide'];
    if (tableCommands.indexOf(cmd.command) > -1) {
      /* Table command */
      scisheet.utilMenuProcessor(eleId, oArgs, "Table", oArgs);
    } else {
      cmd.target = "Sheet";
      /* Sheet command */
      simpleCommands = ['Delete', 'New', 'Redo', 'Undo', 'Unhide'];
      if (simpleCommands.indexOf(cmd.command) > -1) {
        scisheet.utilSendAndReload(cmd);
      } else if (cmd.command === 'Export') {
        scisheetSheet.utilExportDialog(cmd);
      } else if (cmd.command === 'Open') {
        cmd.command = 'ListSheetFiles';
        scisheet.sendServerCommand(cmd, function (names) {
          // User selects the file to open
          scisheetSheet.utilSelectFile(names);
        });
      } else if (cmd.command === 'SaveAs') {
        scisheet.utilPromptForInput(cmd, "Table file name", scisheet.tableFile);
      } else {
        alert("Invalid Sheet command: " + cmd.command);
      }
    }
  };

  this.scisheet.utilClick("SheetClickMenu", oArgs, processClick);
};
