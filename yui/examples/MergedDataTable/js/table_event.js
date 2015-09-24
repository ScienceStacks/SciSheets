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
  alert("Table clicked");
};
