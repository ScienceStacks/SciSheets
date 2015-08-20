/*jslint browser: true */
/*jslint indent: 2 */
/*global $, jQuery, alert */
// Provide for navigation between cells in a table

function myFunc(event) {
  //if (event.keyCode === 9) { //for tab key
  "use strict";
  var currentDiv = event.target;
  $(currentDiv).parents("td").next("td").find("div").click();
  return false;
  //}
}

$(document).ready(function () {
  "use strict";
  $("#mytable td span div").click(function (event) {
    myFunc(event);
  }
    );
});
