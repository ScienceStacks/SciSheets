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

function SciSheets(table) {
  "use strict";
  this.table = function () {}; // Namespace for table functions
  this.column = function () {};  // Namespace for column functions
  this.row = function () {};  // Namespace for row functions
  this.cell = function () {};  // Namespace for cell functions
  this.util = function () {};  // Names space for utility routines.
  this.table = table;
}
