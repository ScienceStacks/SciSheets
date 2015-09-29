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
        var thisEleId, tableMenu;
        thisEleId = event.currentTarget.id;
        alert("Selected " + thisEleId);
        tableMenu = document.getElementById("TableClickMenu");
        $(tableMenu).css("display", "none");
      },
      blur: function (event, data) {
        var tableMenu;
        tableMenu = document.getElementById("TableClickMenu");
        $(tableMenu).hide();
      },
      focus: function (event, data) {
        var tableMenu;
        tableMenu = document.getElementById("TableClickMenu");
        $(tableMenu).show();
      },
    }
  );
  $(ele).css("display", "block");
};
