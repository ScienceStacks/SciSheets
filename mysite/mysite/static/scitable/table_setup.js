/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, SciSheets, SciSheetsColumn, SciSheetsUtilEvent */
/*global $, SciSheetsTable, SciSheetsColumn, SciSheetsRow, SciSheetsCell, DataSource */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */
/*
  TBD:
  1. Make cells editable by default if they are data columns (not formulas)
  2. Assign own click handlers for:
     column: double click - change name
             right click - context menu
     mouseout: detect value change   
   look at http://yuiblog.com/blog/2007/09/26/satyam-datatable-2/
*/


/*
  This file sets up the table and event handlers.
  The table objects are: Table, Column, Row, and Cell. They are specified
  as follows:
    Table - GUID
    Column - name
    Row - number
    Cell - column ID, row ID

  This code provides the following:
    1. Determines when there is a left or right click on the a table object and record
       its identity.
    2. Perform simple local actions and report what is done to the server. This includes
       - Update a data value
       - Change the name of a Table or Column
       - Change a row number
*/
var sciSheets = new SciSheets();

YAHOO.util.Event.addListener(window, "load", function () {
  "use strict";
  YAHOO.example.InlineCellEditing = (function () {
    var myDataTable, highlightEditableCell, myDataSource,
      id, tableElement, d, captionElement, div_ele;
    d = new DataSource();
    div_ele = document.getElementById("TagReplacedByJS");
    $(div_ele).attr('id', d.tableId);

    /* ----------- Code independent of data --------------*/
    // Custom formatter for "address" column to preserve line breaks
    myDataSource = new YAHOO.util.DataSource(d.dataSource);
    myDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
    myDataSource.responseSchema = {
      fields: d.columnDefs
    };
    myDataTable = new YAHOO.widget.DataTable(d.tableId, d.columnDefs, myDataSource,
      {
        caption: d.tableCaption
      }
        );
    sciSheets.setup(myDataTable);

    // Set up events
    highlightEditableCell = function (oArgs) {
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

    /*------------------- Catch cell modifications --------------*/
    myDataTable.subscribe("cellUpdateEvent", function (oArgs) {
      var ep;
      ep = new sciSheets.util.eventProcessing(sciSheets, oArgs);
      sciSheets.cell.modify(ep);
      alert("Modified");
    });

    /* --------------- Catch cell clicks ------------------------*/
    // This logic routes the event to processing a row or a data cell
    //   this - table
    //   this.getColumn(target).field - returns the column name (string)
    //   this.getCellIndex(target) - returns int of 0 based column
    //   this.getRecordIndex(target) - returns an int of 0 based row
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
