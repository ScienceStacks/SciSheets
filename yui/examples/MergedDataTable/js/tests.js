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

function clickTester(clickElement, clickMenuName, selIndex) {
  "use strict";
  var clickMenu, selectEle;
  // Bring up the menu
  $(clickElement).trigger('click');
  clickMenu = document.getElementById(clickMenuName);
  selectEle = clickMenu.children[selIndex];
  $(selectEle).trigger("click");
}

QUnit.test("table_setup", function (assert) {
  "use strict";
  var ele;
  // Mock the server communication
  $.mockjax({
    url: "*",
    responseText: {
      status: "success"
    }
  });
  /* Table Tests */
  ele = document.getElementsByTagName("caption")[0];
  clickTester(ele, "TableClickMenu", 0);
  clickTester(ele, "TableClickMenu", 1);
  assert.ok(true, "Table tests");
  /* Column Tests */
  ele = document.getElementById("yui-dt4-th-name");
  clickTester(ele, "ColumnClickMenu", 0);
  clickTester(ele, "ColumnClickMenu", 1);
  clickTester(ele, "ColumnClickMenu", 2);
  assert.ok(true, "Column tests");
});
