/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, SciSheets, SciSheetsSheet, SciSheetsUtilEvent */
/*global YUI */
/*global $, sciSheets, SciSheetsTable, SciSheetsColumn, SciSheetsRow, SciSheetsCell, DataSource */
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
YAHOO.util.Event.addListener(window, "load", function () {
  "use strict";
  // Reload the page if it's not the base URL.
  // The server knows the current table
  if (window.location.href !== sciSheets.baseURL) {
    sciSheets.utilReload();
  }
  YAHOO.example.InlineCellEditing = (function () {
    var myDataTable, highlightEditableCell, myDataSource, tableHeader,
      id, tableElement, d, captionElement, div_ele, columnDefs;
    d = new DataSource();
    div_ele = document.getElementById("TagReplacedByJS");
    $(div_ele).attr('id', d.tableId);

    /* ----------- Code independent of data --------------*/
    // Custom formatter for "address" column to preserve line breaks
    columnDefs = sciSheets.createColumnDefinitions(d.columnHierarchy);
    myDataSource = new YAHOO.util.DataSource(d.dataSource);
    myDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
    myDataSource.responseSchema = {
      fields: d.responseSchema
    };
    tableHeader = d.tableCaption + " (Table File: " + d.tableFile + ")";
    myDataTable = new YAHOO.widget.DataTable(d.tableId, columnDefs, myDataSource,
      {
        caption: tableHeader,
        selectionMode: "single",
        draggableColumns: true
      }
        );
    sciSheets.setup(myDataTable, d.responseSchema);
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
    myDataTable.subscribe("headerCellMouseoverEvent", function (oArgs) {
      var ele, ep, newLabel, startPos;
      ele = oArgs.target;
      ep = new SciSheetsUtilEvent(sciSheets, oArgs);
      if (ele.innerText === "...") {
        newLabel = ep.columnName;
        // Need to parse columnName
        while (newLabel.indexOf("-") > -1) {
          startPos = newLabel.indexOf("-") + 1;
          newLabel = newLabel.substr(startPos, newLabel.length);
        }
        ele.innerText = "..." + newLabel + "...";
      }
    });
    myDataTable.subscribe("cellMouseoutEvent", myDataTable.onEventUnhighlightCell);
    id = '#' + d.tableId;
    tableElement = $(id);
    captionElement = tableElement.find('caption');

    /*---------------- Catch Sheet clicks (caption)  --------------*/
    captionElement.click(function (oArgs) {
      var sciSheetsSheet;
      sciSheetsSheet = new SciSheetsSheet(sciSheets);
      /* Sheet will redirect Table commands. */
      sciSheetsSheet.click(oArgs);
    });

    /*--------------- Catch column and Table clicks  --------------*/
    myDataTable.subscribe("theadCellClickEvent", function (oArgs) {
      var sciSheetsTable;
      sciSheetsTable = new SciSheetsTable(sciSheets);
      /* Table will redirect to Column handler. */
      sciSheetsTable.click(oArgs);
    });

    /* --------------- Catch cell clicks ------------------------*/
    // This logic routes the event to processing a row or a data cell
    //   this - table
    // oArgs depends on the environment of the click
    myDataTable.subscribe("cellClickEvent", function (oArgs) {
      var ep, sciSheetsRow, sciSheetsCell, scisheets;
      scisheets = sciSheets;
      ep = new SciSheetsUtilEvent(sciSheets, oArgs);
      if (ep.columnLabel === scisheets.ROWNAME) {
        sciSheetsRow = new SciSheetsRow(sciSheets);
        sciSheetsRow.click(oArgs);
      } else {
        sciSheetsCell = new SciSheetsCell(sciSheets);
        sciSheetsCell.click(oArgs);
      }
    });

    return {
      oDS: myDataSource,
      oDT: myDataTable
    };
  }());
});
