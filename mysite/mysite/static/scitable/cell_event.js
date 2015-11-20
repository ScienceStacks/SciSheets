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
  var ep, msg, cmd, scisheet;
  scisheet = this.scisheet;
  ep = new SciSheetsUtilEvent(scisheet, oArgs);
  scisheet.dataTable.on('editorSaveEvent', function (oArgs) {
    //var key = oArgs.editor.getColumn().key;
    msg = "Clicked cell = (" + ep.rowIndex + ", " + ep.columnIndex + ").";
    msg += " Old data: "  + oArgs.oldData + ".";
    msg += " New data: "  + oArgs.newData + ".";
    console.log(msg);
    cmd = scisheet.createServerCommand();
    cmd.command = "Update";
    cmd.target = "Cell";
    cmd.column = ep.columnIndex;
    cmd.row = ep.rowIndex;
    cmd.value = oArgs.newData;
    scisheet.sendServerCommand(cmd, function (data) {
      console.log("Returned: " + data);
    });
  });
  this.scisheet.dataTable.onEventShowCellEditor(oArgs);
};
