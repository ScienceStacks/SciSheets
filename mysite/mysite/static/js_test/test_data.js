
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
  this.tableCaption = 'New table';
  this.tableId = 'scitable';
  this.responseSchema = ['row', 'name', 'address', 'dollars', 'yen'];
  this.columnHierarchy = [{name: 'row', children: []},
      {name: 'name', children: []},
      {name: 'address', children: []},
      {name: 'salary', children: [
      {name: 'dollars', children: []},
      {name: 'yen', children: []}
    ]}
    ];
  this.dataSource = [
    ['1', 'John A. Smith', '1236 Some Street', '12.33', '50'],
    ['2', 'Joan B. Jones', '3271 Another Ave', '34556', '50'],
    ['3', 'Bob C. Uncle', '9996 Random Road', '893', '50'],
    ['4', 'John D. Smith', '1623 Some Street', '0.092', '50'],
    ['5', 'Joan E. Jones', '3217 Another Ave', '23456', '50']
  ];
  this.epilogue = '# Epilogue ';
  this.prologue = '# Prologue';
  this.tableFile = 'scisheet_table';
  this.formulas = {row: '', name: '', address: '', salary: '',
      dollars: '', yen: ''};
}



function newDataSource() {
  "use strict";
  var sciSheets;
  sciSheets = new SciSheets();
  this.tableCaption = "Demo";
  this.tableId = "scitable";
  this.responseSchema = ["Col_0", "Col_1"];
  this.columnDefs = [ {key: "row", formatter: sciSheets.formatColumn("row"), editor:  new YAHOO.widget.TextareaCellEditor(),
    children: [
      {key: "Col_0", formatter: sciSheets.formatColumn("Col_0"), editor:  new YAHOO.widget.TextareaCellEditor()},
      {key: "Col_1", formatter: sciSheets.formatColumn("Col_1"), editor:  new YAHOO.widget.TextareaCellEditor()}
    ]}
     ];
  this.dataSource = [
    ['PPHYr', '1'],
    ['FftSf', '82'],
    ['nAuVf', '48']
  ];
  this.epilogue = "# Epilogue ";
  this.prologue = "# Prologue";
  this.tableFile = 'scisheet_table';
  this.formulas = { "Col_0": '', "Col_1": '', "row": '', "dummy_key": "dummy_value"};
}
