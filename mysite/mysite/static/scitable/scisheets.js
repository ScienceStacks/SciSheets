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
  this.mock_ajax = false;
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

// Factory to create SeverCommand objects (a JSON structure)
// Returns a command object
SciSheets.prototype.createServerCommand = function () {
  "use strict";
  return {command: null,
          target: null,  // Part of table targeted
          table: null,   // Table name
          column: null,
          row: null,
          args: [],
          value: null
         };
};

/* --------------------------------------------------------------- 
  Sends a ServerCommand object to the sever
   Assumes that a JSON object is returned from the server.
      success: boolean that indicates if processing was successful
      data: string returned from server
   Input: serverCommand - a ServerCommand object
          successFunction - function to execute if successful
            The function has a single argument that is the
            string value returned from the server.
   Usage example:
      var scisheets = new SciSheets();
      var data = scisheets.createServerCommand();
      data.command = "delete";
      data.table = "my table";
      data.column = "-3";
      var aSuccessFunction = function (return_data) {
        "use strict";
        alert(return_data);
        window.console.log('Successful');
      };
      scisheets.sendServerCommand(data, aSuccessFunction);
--------------------------------------------------------------- */
SciSheets.prototype.sendServerCommand = function (serverCommand, successFunction) {
  "use strict";
  if (!this.mock_ajax) {
    $.ajax({async: true,
      url: "command",
      data: serverCommand,
      success: function (result) {
        if (!result.success) {
          alert("Server error for cmd: " + serverCommand.command);
        }
        successFunction(result.data);
      },
      error: function (xhr, ajaxOptions, thrownError) {
        alert(xhr.status);
        alert(thrownError);
      }
      });
  }
};

// EventProcessing Object
function SciSheetsUtilEvent(scisheet, oArgs) {
  "use strict";
  var table;
  this.scisheet = scisheet;
  table = this.scisheet.dataTable;
  this.target = oArgs.target;
  this.columnName = table.getColumn(this.target).field;
  this.columnIndex = oArgs.target.cellIndex;
  // this.columnIndex = table.getCellIndex(this.target) + 1;
  this.rowIndex = table.getRecordIndex(this.target) + 1;
}

// Generic click handle for a popup menu
// Input: eleId - ID of the popup menu to use
//        selectedEleFunc - function that processes the selected element
//            argument - ID of the selected element
// Output: establishes the click handlers
function SciSheetsUtilClick(eleId, selectedEleFunc) {
  "use strict";
  var clickMenu;
  clickMenu = document.getElementById(eleId);
  $(clickMenu).menu(
    {
      role: "listbox",
      select: function (event, data) {
        selectedEleFunc(event.currentTarget.firstChild.data);
        $(clickMenu).css("display", "none");
      },
      blur: function (event, data) {
        $(clickMenu).css("display", "none");
      },
      focus: function (event, data) {
        $(clickMenu).css("display", "block");
      },
    }
  );
  $(clickMenu).css("display", "block");
}
