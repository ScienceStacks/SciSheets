/*jshint newcap: true */
/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, QUnit, sciSheets */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

/*
  Constants
*/

var CELL_1_1 = "1", CELL_1_2 = "John A. Smith";


/* 
   Clicks on the specified option on the menu
   If selIndex < 0, then clicks on all
   Inputs: clickEle - element whose click causes the popup menu
           clickMenuName - name of the menu that gets popped up
           selIndex - index of popup options to tests (-1 is all)
*/
function clickTester(clickEle, clickMenuId, selIndex) {
  "use strict";
  var clickMenu, selectEle, i, idx,
    selLst = [];
  // Bring up the menu
  clickMenu = document.getElementById(clickMenuId);
  if (selIndex < 0) {
    for (i = 0; i < clickMenu.children.length; i++) {
      selLst.push(i);
    }
  } else {
    selLst.push(selIndex);
  }
  for (i = 0; i < selLst.length; i++) {
    idx = selLst[i];
    $(clickEle).trigger('click');
    selectEle = clickMenu.children[idx];
    $(selectEle).trigger("click");
  }
}

QUnit.test("table_setup", function (assert) {
  "use strict";
  var caption, ele2, ele3, data_table, cell_1_1, cell_1_2;
  /* Mock Ajax */
  sciSheets.mock_ajax = true;
  /* Table Tests */
  caption = document.getElementsByTagName("caption")[0];
  clickTester(caption, "TableClickMenu", -1);  // Do all items
  assert.ok(caption !== null, "Table tests");
  /* Column Tests */
  ele2 = document.getElementById("yui-dt4-th-row");
  clickTester(ele2, "NameColumnClickMenu", -1);  // Do all items
  assert.ok(ele2 !== null, "Name column tests");
  ele3 = document.getElementById("yui-dt4-th-name");
  clickTester(ele3, "ColumnClickMenu", -1);  // Do all items
  assert.ok(ele3 !== null, "Other column tests");
  /* Get cell elements */
  data_table = document.getElementsByClassName("yui-dt-data")[0];
  cell_1_1 = data_table.getElementsByTagName("pre")[0];
  assert.ok(cell_1_1.innerHTML === CELL_1_1, "Verify cell 1,1");
  cell_1_2 = data_table.getElementsByTagName("pre")[1];
  assert.ok(cell_1_2.innerHTML === CELL_1_2, "Verfiy cell 1,2");
  /* Test the Row menu */
  clickTester(cell_1_1, "RowClickMenu", -1);  // Do all items
  /* Test the Cell menu */
  $(cell_1_2).trigger('click');
  /*
  // Eliminate the cell menu by pressing cancel.
  // Used if load the web page instead of running in batch
  focus = document.activeElement;
  cancel_button = focus.nextElementSibling.childNodes[1];
  $(cancel_button).trigger("click");
  */
});
