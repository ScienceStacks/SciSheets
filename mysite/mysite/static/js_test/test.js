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

/* 
   Clicks on the specified option on the menu
   If selIndex < 0, then clicks on all
*/
function clickTester(clickElement, clickMenuName, selIndex) {
  "use strict";
  var clickMenu, selectEle, i, idx,
    selList = [];
  // Bring up the menu
  clickMenu = document.getElementById(clickMenuName);
  if (selIndex < 0) {
    for (i = 0; i < clickMenu.children.length; i++) {
      selList.push(i);
    }
  } else {
    selList.push(selIndex);
  }
  for (i = 0; i < selList.length; i++) {
    idx = selList[i];
    $(clickElement).trigger('click');
    selectEle = clickMenu.children[idx];
    $(selectEle).trigger("click");
  }
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
  try {
    /* Table Tests */
    ele = document.getElementsByTagName("caption")[0];
    clickTester(ele, "TableClickMenu", -1);  // Do all items
    assert.ok(true, "Table tests");
    /* Column Tests */
    ele = document.getElementById("yui-dt4-th-row");
    clickTester(ele, "FirstColumnClickMenu", -1);  // Do all items
    assert.ok(true, "First column tests");
    ele = document.getElementById("yui-dt4-th-name");
    clickTester(ele, "ColumnClickMenu", -1);  // Do all items
    assert.ok(true, "Other column tests");
    /* Test the Row menu */
    ele = document.getElementById("yui-rec11");
    ele = ele.getElementsByClassName("yui-dt4-col-row")[0];
    clickTester(ele, "RowClickMenu", -1);  // Do all items
    assert.ok(true, "Row tests");
    /* Test the Cell menu */
    ele = document.getElementById("yui-gen26");
    $(ele).trigger('click');
    // Get rid of the menu
    ele = document.getElementById("yui-textareaceditor1-container");
    $(ele).trigger('click');
    assert.ok(true, "Cell tests");
  } catch (err) {
    console.log(err.message);
  }

});
