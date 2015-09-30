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
  This file initializes the SciSheets namespace. The file must preceed all other scisheets javascript files.
  The dependency structure is:
     scisheets - creates the namespaces
     util - common functions
     no other dependencies
*/


/* Create the SciSheets namespace */
function SciSheets() {
  "use strict";
  this.dataTable = null;  // dataTable for this SciSheet
}

// Setup
SciSheets.prototype.setup = function (dataTable) {
  "use strict";
  var ele;
  this.dataTable = dataTable;
  // Handle caption
  ele = document.getElementsByTagName("caption")[0];
  $(ele).css("font-size", "14px");
};

// Data and column setup
SciSheets.prototype.formatColumn = function (name) {
  "use strict";
  var localName = name;
  return function (elCell, oRecord, oColumn, oData) {
    elCell.innerHTML = "<pre class=\"" + localName + "\">" + YAHOO.lang.escapeHTML(oData) + "</pre>";
  };
};

// EventProcessing Object
function SciSheetsUtilEvent(scisheet, oArgs) {
  "use strict";
  var table;
  this.scisheet = scisheet;
  table = this.scisheet.dataTable;
  this.target = oArgs.target;
  this.columnName = table.getColumn(this.target).field;
  this.columnIndex = table.getCellIndex(this.target) + 1;
  this.rowIndex = table.getRecordIndex(this.target) + 1;
}

function zSciSheetsUtilProcessEvent(eleId, selectedEleFunc) {
  "use strict";
  var tableMenu;
  selectedEleFunc(eleId);
  tableMenu = document.getElementById(eleId);
  $(tableMenu).css("display", "none");
}

// Generic click handle for a popup menu
// Input: eleId - ID of the popup menu to use
//        selectedEleFunc - function that processes the selected element
//            argument - ID of the selected element
// Output: establishes the click handlers
function SciSheetsUtilClick(eleId, selectedEleFunc) {
  "use strict";
  var ele;
  // alert(eleId + " clicked");
  ele = document.getElementById(eleId);
  $(ele).menu(
    {
      role: "listbox",
      select: function (event, data) {
        var thisEleId;
        thisEleId = event.currentTarget.id;
        zSciSheetsUtilProcessEvent(thisEleId, selectedEleFunc);
      },
      blur: function (event, data) {
        var tableMenu;
        tableMenu = document.getElementById(eleId);
        $(tableMenu).hide();
      },
      focus: function (event, data) {
        var tableMenu;
        tableMenu = document.getElementById(eleId);
        $(tableMenu).show();
      },
    }
  );
  $(ele).css("display", "block");
}
