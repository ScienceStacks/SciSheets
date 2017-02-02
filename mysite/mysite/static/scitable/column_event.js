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

function SciSheetsColumn(scisheet) {
  "use strict";
  this.scisheet = scisheet;
}

SciSheetsColumn.prototype.click = function (oArgs) {
  "use strict";
  var ep, scisheet, processClick, scisheetColumn;
  scisheetColumn = this;
  scisheet = scisheetColumn.scisheet;

  processClick = function (eleId) {
    scisheet.utilMenuProcessor(eleId, oArgs, "Column");
  };

  ep = new SciSheetsUtilEvent(scisheet, oArgs);
  if (ep.columnLabel  === scisheet.ROWNAME) {
    scisheet.utilClick("NameColumnClickMenu", oArgs, function (eleId, oArgs) {
      var msg;
      msg = "Row Name Column clicked: " + ep.columnName;
      console.log(msg);
      $(ep.target).stop();
    });
  } else {
    scisheet.utilClick("ColumnClickMenu", oArgs, processClick);
  }
};

SciSheetsColumn.prototype.processCommand = function (eleId, oArgs, scisheet) {
  /* 
   * Process commands in the Column menu
   * Input: eleId - element clicked in the menu
   *        oArgs - arguments supplied in Column click
   *        scisheet - SciSheets object
   */
  "use strict";
  var cmd, newPrompt, formula, ep;
  ep = new SciSheetsUtilEvent(scisheet, oArgs);
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
    formula = scisheet.formulas[ep.columnLabel];
    scisheet.utilUpdateFormula(cmd, ep.columnLabel,
        formula, 1, oArgs);
  }
  if (cmd.command === 'Hide') {
    scisheet.utilSendAndReload(cmd);
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
  if (cmd.command === 'Unhide') {
    scisheet.utilSendAndReload(cmd);
  }
};
