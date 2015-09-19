/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */
/*
  TODO:
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

var myColumnDefs, newDataSource, columnNames, tableID, tableCaption;
tableID = "cellediting";
tableCaption = "New table";
columnNames = ["row", "name", "address", "salary"];
myColumnDefs = [
                {key: "row", formatter: SciSheets.util.formatColumn("row"), editor:  new YAHOO.widget.TextareaCellEditor()},
                {key: "name", formatter: SciSheets.util.formatColumn("name"), editor:  new YAHOO.widget.TextareaCellEditor()},
                {key: "address", formatter: SciSheets.util.formatColumn("address"), editor:  new YAHOO.widget.TextareaCellEditor()},
                {key: "salary", formatter: SciSheets.util.formatColumn("salary"), editor:  new YAHOO.widget.TextareaCellEditor()}
               ],
newDataSource = [
    {row: "1", name: "John A. Smith", address: "1236 Some Street", salary: "12.33"},
    {row: "2", name: "Joan B. Jones", address: "3271 Another Ave", salary: "34556"},
    {row: "3", name: "Bob C. Uncle", address: "9996 Random Road", salary: "893"},
    {row: "4", name: "John D. Smith", address: "1623 Some Street", salary: "0.092"},
    {row: "5", name: "Joan E. Jones", address: "3217 Another Ave", salary: "23456"}
                ];

// Common code
YAHOO.util.Event.addListener(window, "load", function () {
  // Custom formatter for "address" column to preserve line breaks
  "use strict";
  YAHOO.example.InlineCellEditing = (function () {
    var myDataTable, highlightEditableCell, myDataSource;
    myDataSource = new YAHOO.util.DataSource(newDataSource);
    myDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
    myDataSource.responseSchema = { 
                                   fields: columnNames
                                  };

    myDataTable = new YAHOO.widget.DataTable(tableID, myColumnDefs, myDataSource,
      {
        caption: tableCaption
      }
        );

    sciSheet = new SciSheets(myDataTable);

    // Set up events
    highlightEditableCell = function (oArgs) {
      var elCell = oArgs.target;
      if (YAHOO.util.Dom.hasClass(elCell, "yui-dt-editable")) {
        this.highlightCell(elCell);
      }
    };
    myDataTable.subscribe("cellMouseoverEvent", highlightEditableCell);
    myDataTable.subscribe("cellMouseoutEvent", myDataTable.onEventUnhighlightCell);
    var id = '#' + tableId;
    var tableElement = $(id);
    var captionElement = tableElement.find('caption');

    /*------------------- Catch table clicks  --------------*/
    captionElement.click(function () {
      var ep, msg;
      ep = new EventProcessing(this, oArgs);
      scisheet.table.click(ep);
      alert("clicked caption");
    });

    /*------------------- Catch column clicks  --------------*/
    myDataTable.subscribe("theadCellClickEvent", function (e) {
      var ep, msg;
      ep = new EventProcessing(this, oArgs);
      scisheet.column.click(ep);
      alert("Column " + ep.columnName + " clicked");
    });

    /*------------------- Catch cell modifications --------------*/
    myDataTable.subscribe("cellUpdateEvent", function (oArgs) { 
      var ep, msg;
      ep = new EventProcessing(this, oArgs);
      scisheet.cell.modified(ep);
      msg = "(r,c) = (" + ep.rowIndex + ", " + ep.columnIndex + ")";
      alert("Modified"); 
    });

    /* --------------- Catch cell clicks ------------------------*/
    // This logic routes the event to processing a row or a data cell
    //   this - table
    //   this.getColumn(target).field - returns the column name (string)
    //   this.getCellIndex(target) - returns int of 0 based column
    //   this.getRecordIndex(target) - returns an int of 0 based row
    myDataTable.subscribe("cellClickEvent", function (oArgs) {
      var ep, msg;
      ep = new EventProcessing(this, oArgs);
      msg = "(r,c) = (" + ep.rowIndex + ", " + ep.columnIndex + ")";
      alert(msg);
      if (columnName === "row") {
        scisheet.row.click(ep);
      }
      else {
        scisheet.cell.click(ep);
        myDataTable.onEventShowCellEditor(oArgs);
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
