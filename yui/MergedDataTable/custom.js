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

var aMenuItems = ["Edit Name", "Clone", "Delete" ];

/*
  Instantiate a ContextMenu:  The first argument passed to the constructor
  is the id for the Menu element to be created, the second is an 
  object literal of configuration properties.
 */
var oEweContextMenu = new YAHOO.widget.ContextMenu("trymenu",
      {
      trigger: ["yui-dt8-th-address", "yui-dt8-th-city"],
      itemdata: aMenuItems,
      lazyload: true
    }
    );

function onEweContextMenuClick(p_sType, p_aArgs) {
/*
  The second item in the arguments array (p_aArgs) 
  passed back to the "click" event handler is the 
  MenuItem instance that was the target of the 
  "click" event.
*/
  "use strict";
  var oItem = p_aArgs[1], // The MenuItem that was clicked
    oTarget = this.contextEventTarget;
  return oItem + oTarget; /* dummy */
}

// "render" event handler for the ewe context menu
//  Add a "click" event handler to the ewe context menu
function onContextMenuRender(p_sType, p_aArgs) {
  "use strict";
  this.subscribe("click", onEweContextMenuClick);
}

// "click" event handler for each item in the ewe context menu
// Add a "render" event handler to the ewe context menu
oEweContextMenu.subscribe("render", onContextMenuRender);


var newDataSource = [
    {name: "John A. Smith", address: "1236 Some Street", city: "San Francisco", state: "CA", amount: 5, active: "yes", colors: ["red"], last_login: "4/19/2007"},
    {name: "Joan B. Jones", address: "3271 Another Ave", city: "New York", state: "NY", amount: 3, active: "no", colors: ["red", "blue"], last_login: "2/15/2006"},
    {name: "Bob C. Uncle", address: "9996 Random Road", city: "Los Angeles", state: "CA", amount: 0, active: "maybe", colors: ["green"], last_login: "1/23/2004"},
    {name: "John D. Smith", address: "1623 Some Street", city: "San Francisco", state: "CA", amount: 5, active: "yes", colors: ["red"], last_login: "4/19/2007"},
    {name: "Joan E. Jones", address: "3217 Another Ave", city: "New York", state: "NY", amount: 3, active: "no", colors: ["red", "blue"], last_login: "2/15/2006"}];

YAHOO.util.Event.addListener(window, "load", function () {
  // Custom formatter for "address" column to preserve line breaks
  "use strict";
  YAHOO.example.InlineCellEditing = (function () {
    var formatAddress = function (elCell, oRecord, oColumn, oData) {
        elCell.innerHTML = "<pre class=\"address\">" + YAHOO.lang.escapeHTML(oData) + "</pre>";
      },
      myColumnDefs = [
        {key: "uneditable"},
        {key: "address", formatter: formatAddress, editor:  new YAHOO.widget.TextareaCellEditor()},
        {key: "city", formatter: "text", editor:  new YAHOO.widget.TextboxCellEditor({disableBtns: true})},
        {key: "state", editor:  new YAHOO.widget.DropdownCellEditor({dropdownOptions: YAHOO.example.Data.stateAbbrs, disableBtns: true})},
        {key: "amount", editor:  new YAHOO.widget.TextboxCellEditor({validator: YAHOO.widget.DataTable.validateNumber})},
        {key: "active", editor:  new YAHOO.widget.RadioCellEditor({radioOptions: ["yes", "no", "maybe"], disableBtns: true})},
        {key: "colors", editor:  new YAHOO.widget.CheckboxCellEditor({checkboxOptions: ["red", "yellow", "blue"]})},
        {key: "fruit", editor:  new YAHOO.widget.DropdownCellEditor({multiple: true, dropdownOptions: ["apple", "banana", "cherry"]})},
        {key: "last_login", formatter: YAHOO.widget.DataTable.formatDate, editor:  new YAHOO.widget.DateCellEditor()}
      ],
      myDataSource = new YAHOO.util.DataSource(YAHOO.example.Data.addresses);
    myDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
    myDataSource.responseSchema = {
      fields: ["address", "city", "state", "amount", "active", "colors", "fruit", {key: "last_login", parser: "date"}]
    };
  
    var myDataTable = new YAHOO.widget.DataTable("cellediting", myColumnDefs, myDataSource, {});
  
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
