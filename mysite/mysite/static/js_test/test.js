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
  This module runs various tests on SciSheets javascript code.
  Note that some of the UI tests don't work in qunit run in the command line.
  Specifically, any test that simulates a click won't happen.

*/

var CELL_1_1 = "1", CELL_1_2 = "John A. Smith";


/* 
   Clicks on the specified option on the menu
   If selIndex < 0, then clicks on all
   Inputs: clickEle - element whose click causes the popup menu
           clickMenuName - name of the menu that gets popped up
           selIndex - index of popup options to tests (-1 is all)
           assert - assert object
           expectedAjaxCalls - int count of Ajax calls made
*/
function clickTester(clickEle,
                     clickMenuId,
                     selIndex,
                     assert,
                     expectedAjaxCalls) {
  "use strict";
  var clickMenu, selectEle, i, idx,
    selLst = [], isOk;
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
    sciSheets.ajaxCallCount = 0;
    idx = selLst[i];
    $(clickEle).trigger('click');
    selectEle = clickMenu.children[idx];
    $(selectEle).trigger("click");
    isOk = sciSheets.ajaxCallCount >= expectedAjaxCalls[idx];
    if (!isOk) {
      alert("Not ok for " + MenuId + " " + selectEle.innerText);
    }
    assert.ok(isOk, "clickTester");
  }
}

// These tests only verify that there is no exception
// when clicking through the menu options
QUnit.test("sheet_setup", function (assert) {
  "use strict";
  var caption, ele2, ele3, data_table, cell_1_1, cell_1_2,
    expectAjaxCalls,
    treeColumns = [{
      "name": "root",
      "children": [
        {"name": "child1", "children": []},
        {"name": "child2", "children": []}
      ]
    }],
    columnDefinitions;
  /* Mock Ajax */
  sciSheets.mockAjax = true;
  /* Sheet Tests */
  caption = document.getElementsByTagName("caption")[0];
  assert.ok(caption !== null, "Verify sheet caption");
  expectAjaxCalls = [1,  // Delete
                    1,  // Epilogue
                    1,  // Export
                    1,  // New
                    1,  // Open
                    1,  // Prologue
                    1,  // Redo
                    1, // Rename
                    1, // SaveAs
                    1, // Trim
                    1, // Undo
                    1]; // UnhideAll
  clickTester(caption, "SheetClickMenu", -1, assert,
      expectAjaxCalls);
  /* Table Tests */
  expectAjaxCalls = [1,  // Append
                    1,  // Delete
                    1,  // Hide
                    1,  // Insert
                    1,  // Move
                    1,  // Refactor
                    1, // Rename
                    1, // Tablize
                    1, // Trim
                    1]; // Unhide
  /* Do Later: Need a nested table to test this
  clickTester(caption, "TableClickMenu", -1, assert,
      expectAjaxCalls);
  */
  // Column Tests
  // If the number of columns is changed from n to m, 
  // must change dt<n> to dt<m>.
  ele2 = document.getElementById("yui-dt6-th-row");
  assert.ok(ele2 !== null, "Verify click element for name row");
  ele3 = document.getElementById("yui-dt6-th-name");
  assert.ok(ele3 !== null, "Verify click element for menu");
  expectAjaxCalls = [
    1, // Append
    1,  // Delete
    1, // Formula
    1, // Hide
    1, // Insert
    1, // Move
    1,  // Refactor
    1,  // Rename
    1,  // Tablize
    1  // Unhide
  ];
  // The following tests fail in batch mode
  clickTester(ele3, "ColumnClickMenu", -1, assert,
      expectAjaxCalls);
  // Row tests
  data_table = document.getElementsByClassName("yui-dt-data")[0];
  cell_1_1 = data_table.getElementsByTagName("pre")[0];
  assert.ok(cell_1_1.innerHTML === CELL_1_1, "Verify cell 1,1");
  expectAjaxCalls = [
    1,   // Append
    1,   // Delete
    0,  // Hide
    1,  // Insert
    1   // Move
  ];
  clickTester(cell_1_1, "RowClickMenu", -1, assert,
      expectAjaxCalls);
  // Cell menu
  cell_1_2 = data_table.getElementsByTagName("pre")[1];
  assert.ok(cell_1_2.innerHTML === CELL_1_2, "Verfiy cell 1,2");
  $(cell_1_2).trigger('click');
  // Function tests
  columnDefinitions = sciSheets.createColumnDefinitions(treeColumns);
  assert.ok(columnDefinitions.length > 0);
});
