/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheetsUtilEvent, SciSheets, $, alert, YAHOO */
/*global SciSheets */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

function SciSheetsCell(scisheet) {
  "use strict";
  this.scisheet = scisheet;
}

SciSheetsCell.prototype.click = function (oArgs) {
  "use strict";
  var ep, scisheet, scisheetCell;
  scisheetCell = this;
  scisheet = scisheetCell.scisheet;
  if (oArgs.target) {
    ep = new SciSheetsUtilEvent(scisheet, oArgs);
    scisheet.dataTable.subscribe('editorCancelEvent', function (editEvent) {
      scisheet.utilReload();
    });
    scisheet.dataTable.subscribe('editorSaveEvent', function (editEvent) {
      var msg, cmd;
      msg = "Clicked cell = (" + ep.rowIndex + ", " + ep.columnName + ").";
      msg += " Old data: "  + editEvent.oldData + ".";
      msg += " New data: "  + editEvent.newData + ".";
      console.log(msg);
      cmd = scisheet.createServerCommand();
      cmd.command = "Update";
      cmd.target = "Cell";
      cmd.columnName = ep.columnName;
      cmd.row = ep.rowIndex;
      cmd.value = editEvent.newData;
      scisheet.utilSendAndReload(cmd);
      scisheet.dataTable.unsubscribe('editorSaveEvent');
    });
    scisheet.dataTable.onEventShowCellEditor(oArgs);
  }
};
