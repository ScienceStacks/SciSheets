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
function doit() {
  'use strict';
  $("#formula-dialog").css("display", "block");
  $("#formula-header").html("New Formula");
  $("#formula-dialog").draggable()
  $("#formula-textarea").linedtextarea({selectedLine: 1});
}

$("#formula-dialog-send").click(function () {
  'use strict';
  var eleTextarea;
  eleTextarea = $("#formula-textarea")[0];
  alert(eleTextarea.value);
  $("#formula-dialog").css("display", "none");
});

$("#formula-dialog-cancel").click(function () {
  'use strict';
  alert("Cancel");
  $("#formula-dialog").css("display", "none");
});
