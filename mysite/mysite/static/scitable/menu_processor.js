/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, SciSheets, SciSheetsColumn, SciSheetsUtilEvent */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

/*
  MenuProcessor provides methods to process command popup menus
  for Sheet, Table, and Column.
  Depends: SciSheets, SciSheetsUtilEvent
*/


/* Create the SciSheets namespace. Values are assigned in sheet_setup.js */
SciSheets.prototype.utilMenuProcessor = function (eleId, oArgs, target) {
  /*
   * eleId - element clicked
   * oArgs - arguments passed to the click processor
   * target - target of the click
   */
  'use strict';
  var cmd, simpleCommands, ep, formula, newPrompt;
  ep = new SciSheetsUtilEvent(this, oArgs);
  console.log(target + " click. Selected " + eleId + ".");
  cmd = this.createServerCommand();
  cmd.command = eleId;
  cmd.columnName = ep.columnName;
  cmd.target = target;
  simpleCommands = ['Delete', 'Hide', 'Trim', 'Unhide', 'UnhideAll'];
  if (simpleCommands.indexOf(cmd.command) > -1) {
    this.utilSendAndReload(cmd);
  } else if (cmd.command === 'Append') {
    this.utilPromptForInput(cmd, "New column name", "");
  } else if (cmd.command === 'Epilogue') {
    this.utilUpdateFormula(cmd, cmd.command,
        this.epilogue, 1, oArgs);
  } else if (cmd.command === 'Formula') {
    formula = this.formulas[ep.columnName];
    this.utilUpdateFormula(cmd, ep.columnName,
        formula, 1, oArgs);
  } else if (cmd.command === 'Insert') {
    this.utilPromptForInput(cmd, "New column name", "");
  } else if (cmd.command === 'Move') {
    this.utilPromptForInput(cmd, "Insert after column", "");
  } else if (cmd.command === 'Prologue') {
    this.utilUpdateFormula(cmd, cmd.command,
        this.prologue, 1, oArgs);
  } else if (cmd.command === 'Refactor') {
    // Change the dialog prompt
    newPrompt = "Refactor column '" + ep.columnName + "': ";
    this.utilPromptForInput(cmd, newPrompt, ep.columnName);
  } else if (cmd.command === 'Rename') {
    this.utilPromptForInput(cmd, "New " + target + " name",
        ep.columnLabel);
  } else if (cmd.command === 'Tablize') {
    // Change the dialog prompt
    newPrompt = "Name of subtable: ";
    this.utilPromptForInput(cmd, newPrompt, "");
  } else if (cmd.command === 'Unhide') {
    this.utilSendAndReload(cmd);
  } else {
    alert("**Invalid command: " + cmd.command);
  }
};
