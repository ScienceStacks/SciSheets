/*jshint newcap: true */
/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, SciSheets */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

/* Creates data objects used elsewhere. Codes is templated. */
function DataSource() {
  "use strict";
  var sciSheets = new SciSheets();
  this.tableId = "cellediting";
  this.tableCaption = "New table";
  this.columnNames = ["row", "name", "address", "salary"];
  this.columnDefs = [
    {key: "row", formatter: sciSheets.formatColumn("row"), editor:  new YAHOO.widget.TextareaCellEditor()},
    {key: "name", formatter: sciSheets.formatColumn("name"), editor:  new YAHOO.widget.TextareaCellEditor()},
    {key: "address", formatter: sciSheets.formatColumn("address"), editor:  new YAHOO.widget.TextareaCellEditor()},
    {key: "salary", formatter: sciSheets.formatColumn("salary"), editor:  new YAHOO.widget.TextareaCellEditor()}
  ];
  this.dataSource = [
    {row: "1", name: "John A. Smith", address: "1236 Some Street", salary: "12.33"},
    {row: "2", name: "Joan B. Jones", address: "3271 Another Ave", salary: "34556"},
    {row: "3", name: "Bob C. Uncle", address: "9996 Random Road", salary: "893"},
    {row: "4", name: "John D. Smith", address: "1623 Some Street", salary: "0.092"},
    {row: "5", name: "Joan E. Jones", address: "3217 Another Ave", salary: "23456"}
  ];
}
