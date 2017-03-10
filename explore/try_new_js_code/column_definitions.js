/*jshint newcap: true */
/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, sciSheets */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

var columns = [
      {name: "p1", children: [{name: "c1", children: []}]},
      {name: "p2", children: []}
    ];

function createColumnDefinitions(treeList) {
  "use strict";
  var columnDefinitions = [], i, thisDefinition, child;
  for (i = 0; i < treeList.length; i++) {
    child = treeList[i];
    thisDefinition = {key: child.name};
    thisDefinition.children = createColumnDefinitions(child.children);
    columnDefinitions.concat([thisDefinition]);
  }
  return columnDefinitions;
}

function oldCreateColumnDefinitions(tree) {
  "use strict";
  var name = tree.name,
    result = {"key": name,
      'formatter': sciSheets.formatColumn(name),
      'editor': new YAHOO.widget.TextareaCellEditor()
      },
    children = tree.children,
    children_result = [],
    child,
    i;

  for (i = 0; i < children.length; i++) {
    child = children[i];
    children_result = 
        children_result.concat(createColumnDefinitions(child));
  }
  result.children = children_result;
  return result;
}

var column_definitions = createColumnDefinitions(columns);
alert('h');
