/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, SciSheets, SciSheetsColumn, SciSheetsUtilEvent */
/*global $, sciSheets, SciSheetsTable, SciSheetsColumn, SciSheetsRow, SciSheetsCell, DataSource */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

function DataSource() {
  "use strict";
  var sciSheets;
  sciSheets = new SciSheets();
  this.tableCaption = "Demo";
  this.tableId = "scitable";
  this.columnDefs =
    [
      {key: "upper",
        formatter: sciSheets.formatColumn("upper"),
        editor:  new YAHOO.widget.TextareaCellEditor(),
        children: [
          {key: "row",
            formatter: sciSheets.formatColumn("row"),
            editor:  new YAHOO.widget.TextareaCellEditor()},
          {key: "Col_0", formatter: sciSheets.formatColumn("Col_0"),
            editor:  new YAHOO.widget.TextareaCellEditor()}
        ]},
      {key: "Col_1", formatter: sciSheets.formatColumn("Col_1"),
        editor:  new YAHOO.widget.TextareaCellEditor()}
    ];
  // Columns with data in them
  this.responseSchema = {
    fields: ["row", "Col_0", "Col_1"]
  };
  // List of values for columns in the responseSchema
  this.dataSource = [
    ["1", "PPHYr", "1"],
    ["2", "FftSf", "82"],
    ["3", "nAuVf", "48"]
  ];
  this.epilogue = "# Epilogue";
  this.prologue = "# Prologue";
  this.tableFile = "scisheet_table";
  this.formulas = { "Col_0": '', "Col_1": '', "row": '', "dummy_key": "dummy_value"};
}

YAHOO.util.Event.addListener(window, "load", function () {
  "use strict";
  // Reload the page if it's not the base URL.
  // The server knows the current table
  YAHOO.example.InlineCellEditing = (function () {
    var myDataTable, highlightEditableCell, myDataSource, tableHeader,
      id, tableElement, d, captionElement, div_ele;
    d = new DataSource();
    div_ele = document.getElementById("TagReplacedByJS");
    $(div_ele).attr('id', d.tableId);

    /* ----------- Code independent of data --------------*/
    // Custom formatter for "address" column to preserve line breaks
    myDataSource = new YAHOO.util.DataSource(d.dataSource);
    myDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
    myDataSource.responseSchema = d.responseSchema;
    tableHeader = d.tableCaption + " (Table File: " + d.tableFile + ")";
    myDataTable = new YAHOO.widget.DataTable(d.tableId, d.columnDefs, myDataSource,
      {
        caption: tableHeader
      }
        );
    sciSheets.setup(myDataTable);
    sciSheets.formulas = d.formulas;
    sciSheets.epilogue = d.epilogue;
    sciSheets.prologue = d.prologue;
    sciSheets.tableFile = d.tableFile;
    sciSheets.tableName = d.tableCaption;

    // Set up events
    highlightEditableCell = function (oArgs) {
      // BUG: oArgs.target doesn't always exist (e.g., if text editor)
      var elCell = oArgs.target;
      if (YAHOO.util.Dom.hasClass(elCell, "yui-dt-editable")) {
        this.highlightCell(elCell);
      }
    };
    myDataTable.subscribe("cellMouseoverEvent", highlightEditableCell);
    myDataTable.subscribe("cellMouseoutEvent", myDataTable.onEventUnhighlightCell);
    id = '#' + d.tableId;
    tableElement = $(id);
    captionElement = tableElement.find('caption');

    /*------------------- Catch table clicks  --------------*/
    captionElement.click(function (oArgs) {
      var sciSheetsTable;
      sciSheetsTable = new SciSheetsTable(sciSheets);
      sciSheetsTable.click(oArgs);
    });

    /*------------------- Catch column clicks  --------------*/
    myDataTable.subscribe("theadCellClickEvent", function (oArgs) {
      var sciSheetsColumn;
      sciSheetsColumn = new SciSheetsColumn(sciSheets);
      sciSheetsColumn.click(oArgs);
    });

    /* --------------- Catch cell clicks ------------------------*/
    // This logic routes the event to processing a row or a data cell
    //   this - table
    // oArgs depends on the environment of the click
    myDataTable.subscribe("cellClickEvent", function (oArgs) {
      var ep, sciSheetsRow, sciSheetsCell;
      ep = new SciSheetsUtilEvent(sciSheets, oArgs);
      if (ep.columnName === "row") {
        sciSheetsRow = new SciSheetsRow(sciSheets);
        sciSheetsRow.click(oArgs);
      } else {
        sciSheetsCell = new SciSheetsCell(sciSheets);
        sciSheetsCell.click(oArgs);
      }
    });


      /* Mutation
      table.addRow({ item: 'collet', cost: 0.42, price: 2.65 });
      
      table.addRows([
          { item: 'nut',    cost: 0.42, price: 2.65 },
          { item: 'washer', cost: 0.01, price: 0.08 },
          { item: 'bit',    cost: 0.19, price: 0.97 }
      ]);
      
      // Remove table records by their Model, id, clientId, or index
      table.removeRow(0);
      
      // Modify a record by passing its id, clientId, or index, followed by an
      // object with new field values
      table.modifyRow('record_4', { cost: 0.74 });
      */

    return {
      oDS: myDataSource,
      oDT: myDataTable
    };
  }());
});
