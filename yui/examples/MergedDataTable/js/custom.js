/*
  TODO:
  1. Make cells editable by default if they are data columns (not formulas)
  2. Assign own click handlers for:
     column: double click - change name
             right click - context menu
     mouseout: detect value change   
   look at http://yuiblog.com/blog/2007/09/26/satyam-datatable-2/
*/

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

// Identify what element was single clicked, specifying the object
$(document).click(function (event) {
  "use strict";
  //  Can reliably find the column by looking for text
  //       equal to the column name. But this can be confused
  //       with the cell contents.
  var dt_type = event.target.className,
    text = $(event.target).text(),
    msg = "Label is " + dt_type + ". Label is " + text;
  if (dt_type === "yui-dt-label") {
    alert(msg);
  }
  event.stopPropagation();
});

// Identify what element was double clicked
$(document).dblclick(function (event) {
  "use strict";
  // TODO: set up click handler, initially just reporting the element
});

var colMenuItems = ["Rename", "Delete" ];
var tblMenuItems = ["Rename", "Delete", "Add-Col" ];

/*
  Instantiate a ContextMenu:  The first argument passed to the constructor
  is the id for the Menu element to be created, the second is an 
  object literal of configuration properties.
 */
// BUG: Not getting the correct DOM element. Consider putting trigger on the table and then not bubbling for column?
var el = $("caption");
var tblContextMenu = new YAHOO.widget.ContextMenu("tab-menu",
      {
      trigger: [ el ],  // Templatetize dt{#columns} & iterate across column names
      itemdata: tblMenuItems,
      lazyload: true
    }
    );

var colContextMenu = new YAHOO.widget.ContextMenu("col-menu",
      {
      trigger: ["yui-dt4-th-address", "yui-dt4-th-salary"],  // Templatetize dt{#columns} & iterate across column names
      itemdata: colMenuItems,
      lazyload: true
    }
    );


function onTblContextMenuClick(p_sType, p_aArgs) {
/*
  The second item in the arguments array (p_aArgs) 
  passed back to the "click" event handler is the 
  MenuItem instance that was the target of the 
  "click" event.
*/
  "use strict";
  var oItem = p_aArgs[1], // The MenuItem that was clicked
    oTarget = this.contextEventTarget;
  alert("Invoked table context menu");
  return oItem + oTarget; /* dummy */
}

function onColContextMenuClick(p_sType, p_aArgs) {
/*
  The second item in the arguments array (p_aArgs) 
  passed back to the "click" event handler is the 
  MenuItem instance that was the target of the 
  "click" event.
*/
  "use strict";
  var oItem = p_aArgs[1], // The MenuItem that was clicked
    oTarget = this.contextEventTarget;
  alert("Invoked column context menu");
}

// "render" event handler for the ewe context menu
//  Add a "click" event handler to the ewe context menu
function onColContextMenuRender(p_sType, p_aArgs) {
  "use strict";
  this.subscribe("click", onColContextMenuClick);
}

function onTblContextMenuRender(p_sType, p_aArgs) {
  "use strict";
  this.subscribe("click", onTblContextMenuClick);
}

// "click" event handler for each item in the ewe context menu
// Add a "render" event handler to the ewe context menu
tblContextMenu.subscribe("render", onTblContextMenuRender);
colContextMenu.subscribe("render", onColContextMenuRender);


var newDataSource = [
    {row: "1", name: "John A. Smith", address: "1236 Some Street", salary: "12.33"},
    {row: "2", name: "Joan B. Jones", address: "3271 Another Ave", salary: "34556"},
    {row: "3", name: "Bob C. Uncle", address: "9996 Random Road", salary: "893"},
    {row: "4", name: "John D. Smith", address: "1623 Some Street", salary: "0.092"},
    {row: "5", name: "Joan E. Jones", address: "3217 Another Ave", salary: "23456"}];

YAHOO.util.Event.addListener(window, "load", function () {
  // Custom formatter for "address" column to preserve line breaks
  "use strict";
  YAHOO.example.InlineCellEditing = (function () {
    function formatColumn(name) {
      var localName = name;
      return function (elCell, oRecord, oColumn, oData) {
        elCell.innerHTML = "<pre class=\"" + localName + "\">" + YAHOO.lang.escapeHTML(oData) + "</pre>";
      };
    }
    var myDataTable, highlightEditableCell,
      format_address = formatColumn("address"),
      format_name = formatColumn("name"),
      format_row = formatColumn("row"),
      format_salary = formatColumn("salary"),
      myColumnDefs = [
        {key: "row", formatter: format_row, editor:  new YAHOO.widget.TextareaCellEditor()},
        {key: "name", formatter: format_name, editor:  new YAHOO.widget.TextareaCellEditor()},
        {key: "address", formatter: format_address, editor:  new YAHOO.widget.TextareaCellEditor()},
        {key: "salary", formatter: format_salary, editor:  new YAHOO.widget.TextareaCellEditor()}
      ],
      myDataSource = new YAHOO.util.DataSource(newDataSource);
    myDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
    myDataSource.responseSchema = {
      fields: ["row", "name", "address", "salary"]
    };

    myDataTable = new YAHOO.widget.DataTable("cellediting", myColumnDefs, myDataSource,
      {
        caption: "New table"
      }
        );

    // Set up editing flow
    highlightEditableCell = function (oArgs) {
      var elCell = oArgs.target;
      if (YAHOO.util.Dom.hasClass(elCell, "yui-dt-editable")) {
        this.highlightCell(elCell);
      }
    };
    myDataTable.subscribe("cellMouseoverEvent", highlightEditableCell);
    myDataTable.subscribe("cellMouseoutEvent", myDataTable.onEventUnhighlightCell);
    // myDataTable.subscribe("cellClickEvent", myDataTable.onEventShowCellEditor);

    myDataTable.subscribe("cellClickEvent", function (oArgs) {
        var target = oArgs.target,
            record = this.getRecord(target),
            column = this.getColumn(target);
     
        switch (column.key) {
            // Do stuff here
        }
    });

    return {
      oDS: myDataSource,
      oDT: myDataTable
    };
  }());
});
