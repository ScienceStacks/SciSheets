/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global SciSheets, $, alert, YAHOO */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

function SciSheetsTable(scisheet) {
  "use strict";
  this.scisheet = scisheet;
}

SciSheetsTable.prototype.click = function (oArgs) {
  "use strict";
  var ele;
  alert("Table clicked");
  ele = document.getElementById("TableClickMenu");
  $(ele).menu(
    {
      role: "listbox",
      select: function (event, data) {
        var thisEleId, ele;
        thisEleId = event.currentTarget.id;
        alert("Selected " + thisEleId);
        ele = document.getElementById("TableClickMenu");
        $(ele).css("display", "none");
      }
    }
  );
  $(ele).css("display", "block");
};
