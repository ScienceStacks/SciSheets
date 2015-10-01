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

$.mockjax({
  url: "/restful/fortune",
  responseText: {
    status: "failure",
    fortune: "Are you a mock turtle?"
  }
});

$(document).ready(function () {
  "use strict";
  $.getJSON("/restful/fortune", function (response) {
    if (response.status === "success") {
      $("#fortune").html("Your fortune is: " + response.fortune);
    } else {
      $("#fortune").html("Things do not look good, no fortune was told");
    }
  });
});
