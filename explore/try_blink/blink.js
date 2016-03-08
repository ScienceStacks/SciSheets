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

/*
  This file initializes the SciSheets namespace. The file must preceed all other scisheets javascript files.
  The dependency structure is:
     scisheets - creates the namespaces
     util - common functions
     no other dependencies
*/

var mode = 1, blinker, evenClick = true;

/****** Blinker *****/
function SciSheetsBlinker(obj) {
  // Blinks the text object obj
  "use strict";
  this.blink = {
    obj: obj,
    timeout: 15000,
    speed: 1000
  };
  this.fn = null;
  $(this.blink.obj).css("display", "none");
}

SciSheetsBlinker.prototype.start = function () {
  "use strict";
  $(this.blink.obj).css("display", "block");
  this.fn = setInterval(function () {
    this.blink.obj.fadeToggle(this.blink.speed);
  }, this.blink.speed + 1);
};

SciSheetsBlinker.prototype.stop = function () {
  "use strict";
  $(this.blink.obj).css("display", "none");
  $(this.blink.obj).fadeOut();
  clearInterval(this.fn);
};


function clickedMeOne() {
  "use strict";
  if (evenClick) {
    blinker.start();
  } else {
    blinker.stop();
  }
  evenClick = !evenClick;
}


// Alternative code (2)
var blink = {
    obj: $("#notification-working"),
    timeout: 15000,
    speed: 1000
  };

function clickedMeTwo() {
  "use strict";
  if (evenClick) {
    $(blink).css("display", "block");
    blink.fn = setInterval(function () {
      blink.obj.fadeToggle(blink.speed);
    }, blink.speed + 1);
  } else {
    $(blink).css("display", "none");
    setTimeout(function () {
      clearInterval(blink.fn);
    });
  }
  evenClick = !evenClick;
}

if (mode === 1) {
  blinker = new SciSheetsBlinker("#notification-working");
}

function clickedMe() {
  "use strict";
  if (mode === 1) {
    clickedMeOne();
  } else {
    clickedMeTwo();
  }
}
