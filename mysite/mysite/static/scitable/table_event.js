/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheets, $, alert, YAHOO, SciSheetsUtilEvent, SciSheetsColumn */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */
/*jslint newcap: true */

function SciSheetsTable(scisheet) {
  "use strict";
  this.scisheet = scisheet;
}

SciSheetsTable.prototype.click = function (oArgs) {
  "use strict";
  var ep, scisheet, scisheetTable, scisheetColumn, processClick;
  scisheetTable = this;
  scisheet = scisheetTable.scisheet;

  processClick = function (eleId) {
    /* Processes a click on a Table menu */
    /* Input: eleId - menu item selection */
    scisheetTable.processCommand(eleId, oArgs, scisheet);
  };

  ep = new SciSheetsUtilEvent(scisheet, oArgs);
  $(ep.target).effect("highlight", 1000000);
  $(ep.target).toggle("highlight");
  if (scisheet.responseSchema.indexOf(ep.columnName) > -1) {
    /* Check if this is a Column instead of a Table */
    scisheetColumn = new SciSheetsColumn(scisheet);
    scisheetColumn.click(oArgs);
  } else {
    /* Is a table command. */
    scisheet.utilClick("TableClickMenu", oArgs, processClick);
  }
};

SciSheetsTable.prototype.processCommand = function (eleId, oArgs, scisheet) {
  'use strict';
  var cmd, simpleCommands;
  console.log("Table click. Selected " + eleId + ".");
  cmd = scisheet.createServerCommand();
  cmd.command = eleId;
  cmd.target = "Table";
  simpleCommands = ['Append', 'Delete', 'Hide', 'Insert', 'Move',
      'Trim', 'Unhide'];
  if (simpleCommands.indexOf(cmd.command) > -1) {
    scisheet.utilSendAndReload(cmd);
  } else if (cmd.command === 'Epilogue') {
    scisheet.utilUpdateFormula(cmd, cmd.command,
        scisheet.epilogue, 1, oArgs);
  } else if (cmd.command === 'Prologue') {
    scisheet.utilUpdateFormula(cmd, cmd.command,
        scisheet.prologue, 1, oArgs);
  } else if (cmd.command === 'Rename') {
    scisheet.utilPromptForInput(cmd, "New table name",
        scisheet.tableCaption);
  } else {
    alert("**Invalid command: " + cmd.command);
  }
};
