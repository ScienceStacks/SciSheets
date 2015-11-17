/*jshint newcap: true */
/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, SciSheets */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */


/* Example of sending a command and processing the callback. */
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
