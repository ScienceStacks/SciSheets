/*jshint newcap: true */
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
function selectMenu() {
  "use strict";
  var options, names, n, ele, name, selMenu, selFunction;
  // List of selection options
  names = ["opt1", "opt2"];
  selMenu = $("#select-choice-min");
  selFunction = function () {alert(this.id); };
  // Set the id of each option to the file name
  options = "";
  for (n = 0; n <  names.length; n++) {
    name = names[n];
    options = options + "<option id='" + name + "'>"
              + name + "</option>";
  }
  $('select').append(options);
  for (n = 0; n < names.length; n++) {
    ele = "#" + names[n];
    $(ele).click(selFunction);
  }
  $(selMenu).css("display", "block");
  $(selMenu).find('select').selectmenu('refresh');
}
