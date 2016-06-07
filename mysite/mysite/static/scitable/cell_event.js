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
  var ep, scisheet;
  scisheet = this.scisheet;
  if (oArgs.target) {
    ep = new SciSheetsUtilEvent(scisheet, oArgs);
    scisheet.dataTable.subscribe('editorCancelEvent', function (editEvent) {
      scisheet.utilReload();
    });
    scisheet.dataTable.subscribe('editorSaveEvent', function (editEvent) {
      var msg, cmd;
      msg = "Clicked cell = (" + ep.rowIndex + ", " + ep.columnIndex + ").";
      msg += " Old data: "  + editEvent.oldData + ".";
      msg += " New data: "  + editEvent.newData + ".";
      console.log(msg);
      cmd = scisheet.createServerCommand();
      cmd.command = "Update";
      cmd.target = "Cell";
      cmd.column = ep.columnIndex;
      cmd.row = ep.rowIndex;
      cmd.value = editEvent.newData;
      scisheet.utilSendAndReload(cmd);
      scisheet.dataTable.unsubscribe('editorSaveEvent');
    });
    this.scisheet.dataTable.onEventShowCellEditor(oArgs);
  }
};
