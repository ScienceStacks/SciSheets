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
  // TBD: Shorten new table to just a button. Still getting extra space.
  // TBD: Look at JqueryUI to create custom inputs - https://github.com/jquery/jquery-ui - 
 //        especially the model form in the dialogue example.
 //        maybe better off doing this in python?
 // also look at yui - http://yuilibrary.com/ and http://yuilibrary.com/yui/docs/panel/panel-form-example.html
var grid;
var columns = [{id: "table", name: "new-table", field: "name"}];

  for (var i = 0; i < columns.length; i++) {
    columns[i].header = {
      menu: {
        items: [
          {
            title: "Rename",
            command: "rename"
          },
          {
            title: "Add Column",
            command: "add-col"
          },
          {
            iconImage: "../static/sort-asc.gif",
            title: "Sort Ascending",
            command: "sort-asc",
            disabled: true
          },
          {
            iconImage: "../static/sort-desc.gif",
            title: "Sort Descending",
            command: "sort-desc",
            disabled: true
          },
          {
            iconCssClass: "icon-help",
            title: "Help",
            command: "help"
          }
        ]
      }
    };
  }


  var options = {
    enableColumnReorder: false
  };

  $(function () {
    var data = [];

    grid = new Slick.Grid("#myGrid", data, columns, options);

    var headerMenuPlugin = new Slick.Plugins.HeaderMenu({});

    // TODO: Send new name to server
    // TODO: Handle add-col
    headerMenuPlugin.onCommand.subscribe(function(e, args) {
      if (args.command == "rename") {
        var newName = window.prompt('New name?', 'current name');
        args.column.name = newName;
        grid.setColumns(grid.getColumns());
      }
      if (args.command == "add-col") {
        alert(args.command);
      }
    });

    grid.registerPlugin(headerMenuPlugin);

  })
