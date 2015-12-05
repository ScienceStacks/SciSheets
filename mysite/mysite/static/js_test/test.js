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
  var ele1, ele2, ele3, ele4, ele5, ele6, ele7;
  // Mock the server communication
  /*
  $.mockjax({
    url: "*",
    contentType: 'text/json',
    responseText: {
      success: true
    }
  });
  */
  try {
    /* Table Tests */
    ele1 = document.getElementsByTagName("caption")[0];
    clickTester(ele1, "TableClickMenu", -1);  // Do all items
    assert.ok(ele1 != null, "Table tests");
    /* Column Tests */
    ele2 = document.getElementById("yui-dt4-th-row");
    clickTester(ele2, "FirstColumnClickMenu", -1);  // Do all items
    assert.ok(ele2 != null, "First column tests");
    ele3 = document.getElementById("yui-dt4-th-name");
    clickTester(ele3, "ColumnClickMenu", -1);  // Do all items
    assert.ok(ele3 != null, "Other column tests");
    /* Test the Row menu */
    ele4 = document.getElementById("yui-rec11");
    ele5 = ele4.getElementsByClassName("yui-dt4-col-row")[0];
    clickTester(ele5, "RowClickMenu", -1);  // Do all items
    assert.ok(ele5 != null, "Row tests");
    /* Test the Cell menu */
    ele6 = document.getElementById("yui-gen26");
    $(ele6).trigger('click');
    // Get rid of the menu
    ele7 = document.getElementById("yui-textareaceditor1-container");
    $(ele7).trigger('click');
    assert.ok(ele7 != null, "Cell tests");
  } catch (err) {
    console.log(err.message);
    assert.ok(false, "Cell tests failed.");
  }

});
