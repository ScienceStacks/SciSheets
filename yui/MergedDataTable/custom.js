/*jslint indent: 2 */
/*jslint browser: true*/
/*jslint unparam: true*/
/*global $, jQuery, alert, YAHOO */
/*jshint onevar: false */

$(document).click(function (event) {
  "use strict";
  var dt_type = event.target.className,
    text = $(event.target).text(),
    msg = "Label is " + dt_type + ". Label is " + text;
  if (dt_type === "yui-dt-label") {
    alert(msg);
  }
});

var colMenuItems = ["Rename", "Delete" ];
var tblMenuItems = ["Rename", "Delete", "Add-Col" ];

/*
  Instantiate a ContextMenu:  The first argument passed to the constructor
  is the id for the Menu element to be created, the second is an 
  object literal of configuration properties.
 */
// BUG: Not getting the correct DOM element. Consider putting trigger on the table and then not bubbling for column?
var el = $( "caption" );
var tblContextMenu = new YAHOO.widget.ContextMenu("tab-menu",
      {
      trigger: [ el ],  // Templatetize dt{#columns} & iterate across column names
      itemdata: tblMenuItems,
      lazyload: true
    }
    );

var colContextMenu = new YAHOO.widget.ContextMenu("col-menu",
      {
      trigger: ["yui-dt3-th-address", "yui-dt3-th-salary"],  // Templatetize dt{#columns} & iterate across column names
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
  return oItem + oTarget; /* dummy */
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
    {name: "John A. Smith", address: "1236 Some Street", salary: "12.33"},
    {name: "Joan B. Jones", address: "3271 Another Ave", salary: "34556"},
    {name: "Bob C. Uncle", address: "9996 Random Road", salary: "893"},
    {name: "John D. Smith", address: "1623 Some Street", salary: "0.092"},
    {name: "Joan E. Jones", address: "3217 Another Ave", salary: "23456"}];

YAHOO.util.Event.addListener(window, "load", function () {
  // Custom formatter for "address" column to preserve line breaks
  "use strict";
  YAHOO.example.InlineCellEditing = (function () {
    var formatAddress = function (elCell, oRecord, oColumn, oData) {
        elCell.innerHTML = "<pre class=\"address\">" + YAHOO.lang.escapeHTML(oData) + "</pre>";
      },
      myColumnDefs = [
        {key: "name", formatter: formatAddress, editor:  new YAHOO.widget.TextareaCellEditor()},
        {key: "address", formatter: formatAddress, editor:  new YAHOO.widget.TextareaCellEditor()},
        {key: "salary", formatter: formatAddress, editor:  new YAHOO.widget.TextareaCellEditor()}
      ],
      myDataSource = new YAHOO.util.DataSource(newDataSource);
    myDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
    myDataSource.responseSchema = {
      fields: ["name", "address", "salary"]
    };

    var myDataTable = new YAHOO.widget.DataTable("cellediting", myColumnDefs, myDataSource,
        {
          caption: "New table"
        }
        );

    // Set up editing flow
    var highlightEditableCell = function (oArgs) {
      var elCell = oArgs.target;
      if (YAHOO.util.Dom.hasClass(elCell, "yui-dt-editable")) {
        this.highlightCell(elCell);
      }
    };
    myDataTable.subscribe("cellMouseoverEvent", highlightEditableCell);
    myDataTable.subscribe("cellMouseoutEvent", myDataTable.onEventUnhighlightCell);
    myDataTable.subscribe("cellClickEvent", myDataTable.onEventShowCellEditor);
    return {
      oDS: myDataSource,
      oDT: myDataTable
    };
  }());
});
