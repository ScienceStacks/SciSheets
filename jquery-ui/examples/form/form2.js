/*jshint newcap: true */
/*jshint onevar: true */
/*jshint todo: true */
/*jshint qunit: true */
/*jshint jquery: true */
/*jshint yui: true */
/*jslint plusplus: true */
/*jshint onevar: false */
/*global $, alert, YAHOO, CSSStyleDeclaration */
/*jslint unparam: true*/
/*jslint browser: true */
/*jslint indent: 2 */

/*
function css(ele) {
  "use strict";
  var sheets = document.styleSheets, i, rules;
  for (i in sheets) {
    rules = sheets[i].rules || sheets[i].cssRules;
  }
  return rules;
}
*/


$(document).ready(function () {
  "use strict";
  $("#rename-dialog").dialog({
    autoOpen: false,
    modal: true,
    dialogClass: "dlg-no-close",
    buttons: {
      "Submit": function () {
        alert("New name is " + $("#name").val());
        $(this).dialog("close");
      },
      "Cancel": function () {
        $(this).dialog("close");
      }
    }
  });

  $("#button1").on("click", function () {
    $("#rename-dialog").dialog("open");
  });
});
