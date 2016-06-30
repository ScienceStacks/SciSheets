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

/* --------------- Utility objects ------------------*/
/****** Blinker *****/
function SciSheetsBlinker(ele) {
  // Blinks the text eleect ele
  "use strict";
  this.blink = {
    ele: ele,
    speed: 1000
  };
  this.fn = null;
  $(this.blink.ele).css("display", "none");
}

SciSheetsBlinker.prototype.start = function () {
  "use strict";
  var scisheet = this;
  $(this.blink.ele).css("display", "block");
  this.fn = setInterval(function () {
    scisheet.blink.ele.fadeToggle(scisheet.blink.speed);
  }, scisheet.blink.speed + 1);
};

SciSheetsBlinker.prototype.stop = function () {
  "use strict";
  $(this.blink.ele).css("display", "none");
  $(this.blink.ele).fadeOut();
  clearInterval(this.fn);
};


/* --------------- SciSheets Objects ------------------*/

/* Create the SciSheets namespace. Values are assigned in table_setup.js */
function SciSheets() {
  "use strict";
  this.baseURL = "http://localhost:8000/scisheets/";
  this.dataTable = null;  // dataTable for this SciSheet
  this.mockAjax = false;
  this.ajaxCallCount = 0;
  this.formulas = null;  // Dictionary by column name of formulas
  this.epilogue = null;
  this.prologue = null;
  this.tableFile = null;  // No file specified for the table
  this.blinker = new SciSheetsBlinker($("#notification-working"));
  this.tableName = null;
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
  this.ajaxCallCount += 1;
  if (!this.mockAjax) {
    $.ajax({async: true,
      url: "command",
      data: serverCommand,
      success: function (result) {
        var msg;
        if (!result.success) {
          msg = "Error for cmd: " + serverCommand.command;
          msg += "\n" + result.data;
          alert(msg);
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
// Input: scisheet - SciSheets object
//        oArgs - argument provided to the click handler
//                depends on the specific click event
// Returns: Creates a SciSheetsUtil object with fields for
//   this.scisheet - the scisheet processed
//   this.oArgs - the arguments provided
//   this.target - target of click
//   this.columnName - name of the column clicked
//   this.columnIndex - index of the column clicked
//   this.rowIndex - index of the row clicked
function SciSheetsUtilEvent(scisheet, oArgs) {
  "use strict";
  var table;
  this.scisheet = scisheet;
  this.oArgs = oArgs;
  table = scisheet.dataTable;
  if (!oArgs.target) {
    console.log("***Could not process oArgs.");
  } else {
    this.target = oArgs.target;
    this.columnName = table.getColumn(this.target).field;
    this.columnIndex = oArgs.target.cellIndex;
    this.rowIndex = table.getRecordIndex(this.target) + 1;
  }
  this.rowIndex = table.getRecordIndex(this.target) + 1;
}

SciSheets.prototype.utilUpdateFormula = function (cmd, formulaLocation, formula, linePosition, evObj) {
  // Create the dialogue and extract formula changes
  // Input: cmd - AJAX command
  //        formulaLocation (str) - Column/Prologue/Epilogue
  //        formula (str)
  //        linePosition (int) - where the dialogue is positioned
  //        evObj - event object
  "use strict";
  var scisheet, eleTextarea, leftPos, topPos;
  scisheet = this;
  eleTextarea = $("#formula-textarea")[0];
  if (formula !== "") {
    eleTextarea.value = formula;
  }
  if (scisheet.mockAjax) {
    scisheet.ajaxCallCount += 1;  // Count as an Ajax call
  }
  $("#formula-dialog").css("display", "block");
  $("#formula-header").html(formulaLocation);
  $("#formula-dialog").draggable();
  $("#formula-textarea").linedtextarea({selectedLine: linePosition});
  leftPos = evObj.pageX1 + 30;
  topPos = 10;
  // evObj.pageX1, evObj.pageY
  $("#formula-dialog").css({left: leftPos, top: topPos});
  $("#formula-dialog-submit").click(function () {
    cmd.args = [eleTextarea.value];
    $("#formula-dialog").css("display", "none");
    scisheet.utilSendAndReload(cmd);
  });
  $("#formula-dialog-cancel").click(function () {
    $("#formula-dialog").css("display", "none");
    scisheet.utilReload();
  });
};

// Generic click handle for a popup menu
// Input: eleId - ID of the popup menu to use
//        evObj - event object
//        selectedEleFunc - function that processes the selected element
//            argument - ID of the selected element
// Output: establishes the click handlers
SciSheets.prototype.utilClick = function (eleId, evObj, selectedEleFunc) {
  "use strict";
  var clickMenu, scisheet, selected;
  selected = false;
  scisheet = this;
  clickMenu = document.getElementById(eleId);
  $(clickMenu).css({left: evObj.pageX, top: evObj.pageY});
  $(clickMenu).menu(
    {
      role: "listbox",
      select: function (event, data) {
        selected = true;
        selectedEleFunc(event.currentTarget.firstChild.data);
      },
      blur: function (event, data) {
        if (event.handleObj.type === "mouseout") {
          $(clickMenu).hide();
          if (!selected) {
            scisheet.utilReload();  // Eliminate the highlighting
          }
        }
      },
      focus: function (event, data) {
        $(clickMenu).css("display", "block");
      },
    }
  );
  $(clickMenu).css("display", "block");
  $(document).keydown(function (e) {
    if (e.keyCode === 27) {
      $(clickMenu).css("display", "none");
    }
  });
};

SciSheets.prototype.utilReload = function () {
  "use strict";
  if (!this.mockAjax) {
    window.location.href = this.baseURL;
  }
};

SciSheets.prototype.utilSendAndReload = function (cmd) {
  "use strict";
  var scisheet = this;
  this.sendServerCommand(cmd, function (data) {
    scisheet.blinker.start();  // Object is deleted by reload
    console.log("Server returned: " + data);
    scisheet.utilReload();
  });
};

/* ---------- Dialog management ---------------*/
SciSheets.prototype.utilPromptForInput = function (cmd, newPrompt, defaultValue) {
  // Change the dialog prompt
  "use strict";
  var scisheet, response;
  scisheet = this;
  if (scisheet.mockAjax) {
    scisheet.ajaxCallCount += 1;  // Count as an Ajax call
  }
  response = window.prompt(newPrompt, defaultValue);
  if (response !== null) {
    cmd.args = [response];
    scisheet.utilSendAndReload(cmd);
  } else {
    scisheet.utilReload();
  }
};

/* Setup the global variable */
var sciSheets = new SciSheets();
