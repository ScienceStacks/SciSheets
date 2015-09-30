/*jshint newcap: true */
/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, QUnit */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

QUnit.test("table_setup", function (assert) {
  "use strict";
  var ele, clickMenu, selectEle;
  ele = document.getElementsByTagName("caption")[0];
  // Bring up the menu
  $(ele).trigger('click');
  clickMenu = document.getElementById("TableClickMenu");
  // Call directly the code that processes the menu selection
  //clickMenu.selectedIndex = 0;
  //$(clickMenu).trigger("select");
  // selectEle = $(clickMenu).find("rename");
  // selectEle.trigger("select");
  assert.ok(true, "dummy");
});
