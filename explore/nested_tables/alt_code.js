/*jshint newcap: true */
/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, SciSheets */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

var sciSheets = new SciSheets();
var div_ele = document.getElementById("TagReplacedByJS");
$(div_ele).attr('id', "nested");
var data, myColumnDefs, responseSchema;

function data1() {
  "use strict";
  data =
    [
      ["home.html", 20, 400, 44, 657],
      ["blog.html", 24, 377, 97, 567],
      ["contact.html", 32, 548, 42, 543],
      ["about.html", 8, 465, 12, 946],
      ["pagenotfound.html", 0, 0, 0, 0]
    ];
  myColumnDefs =
    [
      {key: "page", label: "Page", sortable: true, resizeable: true},
      {label: "Statistics", formatter: YAHOO.widget.DataTable.formatNumber, children:
          [
          {label: "Visits", children:
            [
              {key: "visitsmonth", label: "This Month", sortable: true, resizeable: true},
              {key: "visitsytd", label: "YTD", abbr: "Year to Date", sortable: true, resizeable: true}
            ]
            },
          {label: "Views", children:
            [
              {key: "viewsmonth", label: "This Month", sortable: true, resizeable: true},
              {key: "viewsytd", label: "YTD", abbr: "Year to Date", sortable: true, resizeable: true}
            ]
            }
        ]
        }
    ];
  responseSchema =
    {
      fields: ["page", "visitsmonth", "visitsytd", "viewsmonth", "viewsytd"]
    };
}

function data2() {
  "use strict";
  myColumnDefs =
    [
      {key: "page"},
      {label: "Upper", formatter: YAHOO.widget.DataTable.formatNumber, children: [
        {label: "Statistics", formatter: YAHOO.widget.DataTable.formatNumber,
          children: [
            {label: "Visits",
              children: [
                {key: "visitsmonth"},
                //{key: "visitsmonth",
                // Looks like this should be done a different way. See web page for
                // DataTable Control: Custom Cell Formatting
                //  formatter: sciSheets.formatColumn("Visits")},
                {key: "visitsytd"}
              ]},
            {label: "Views",
              children: [
                {key: "visitsmonth"},
                {key: "visitsytd"}
              ]}
          ]}
      ]}
    ];

  data =
    [
      ["home.html", 20, 400, 44, 657],
      ["blog.html", 24, 377, 97, 567],
      ["contact.html", 32, 548, 42, 543],
      ["about.html", 8, 465, 12, 946],
      ["pagenotfound.html", 0, 0, 0, 0]
    ];
  responseSchema =
    {
      fields: ["page", "visitsmonth", "visitsytd", "visitsmonth", "visitsytd"]
    };
}

data2();



YAHOO.util.Event.addListener(window, "load", function () {
  "use strict";
  // Reload the page if it's not the base URL.
  // The server knows the current table
  YAHOO.example.InlineCellEditing = (function () {
    var XXmyDataSource = new YAHOO.util.DataSource(data);
    XXmyDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
    XXmyDataSource.responseSchema = responseSchema;
    var XXmyDataTable = new YAHOO.widget.DataTable(div_ele, myColumnDefs, XXmyDataSource);
  }());
});
