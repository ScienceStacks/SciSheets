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

$(function() {
    $("#submit_btn").click(function() {
      alert("Done button");
    });
  });

$(function() {
    $("#cancel_btn").click(function() {
      var ele_form = $("#myform");
      alert("Cancel button");
      ele_form.css("display", "none");
      $("#myform").css("display", "none");
    });
  });
