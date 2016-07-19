/*jshint newcap: true */
/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, YAHOO */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */


YUI().use("datatable-base", function (Y) {
  'use strict';
  var nestedCols, data, dt;
  nestedCols = [
    {key: "Schedule"},
    {key: "Details", children: [
      {key: "track"},
      {label: "Route", children: [
        {key: "from"},
        {key: "to"}
      ]}
    ]}
  ];
  data = [
    {Schedule: "A", track: "1", from: "Paris", to: "Amsterdam"},
    {Schedule: "B", track: "2", from: "Paris", to: "London"},
    {Schedule: "C", track: "3", from: "Paris", to: "Zurich"}
  ];
  dt = new Y.DataTable({
    columns: nestedCols,
    data   : data,
    summary: "Train schedule",
    caption: "Table with nested column headers"
  }).render("#nested");
});
