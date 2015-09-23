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
  this.dataTable = null;  // dataTable for this SciSheet
}

SciSheets.prototype.util = function() {};
SciSheets.prototype.table = function() {};
SciSheets.prototype.row = function() {};
SciSheets.prototype.column = function() {};
SciSheets.prototype.column = function() {};
SciSheets.prototype.cell = function() {};
