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



YAHOO.example.Data = {bookorders:
    [{id: "po-0167", date: new Date(1980, 2, 24),
      quantity: 1, amount: 4, title: "A Book About Nothing"},
     {id: "po-0783", date: new Date("January 3, 1983"),
      quantity: null, amount: 12.12345, title: "The Meaning of Life"},
     {id: "po-0297", date: new Date(1978, 11, 12),
      quantity: 12, amount: 1.25,
      title: "This Book Was Meant to Be Read Aloud"},
     {id: "po-1482", date: new Date("March 11, 1985"),
      quantity: 6, amount: 3.5, title: "Read Me Twice"}]};

YAHOO.util.Event.addListener(window, "load", function () {
  "use strict";
  YAHOO.example.ReorderRows = (function () {
    var Dom = YAHOO.util.Dom,
      Event = YAHOO.util.Event,
      DDM = YAHOO.util.DragDropMgr,
      myColumnDefs = [{key: "id"},
                      {key: "date", formatter: "date"},
                      {key: "quantity", formatter: "number"},
                      {key: "amount", formatter: "currency"},
                      {key: "title"}],
      myDataSource = new YAHOO.util.LocalDataSource(YAHOO.example.Data.bookorders,
          {responseSchema: {fields: ["id", "date", "quantity", "amount", "title"]}}),
      myDataTable = new YAHOO.widget.DataTable("datatable", myColumnDefs, myDataSource, {caption: "YUI Datatable/DragDrop"}),
      myDTDTargets = {},
      onColumnSelect = function (ev) {
        var par = myDataTable.getThEl(Event.getTarget(ev)),
          srcData,
          srcIndex,
          tmpIndex = null,
          ddCol = new YAHOO.util.DDProxy(par.id);
        ddCol.handleMouseDown(ev.event);
        /**
        * Once we start dragging a row, we make the proxyEl look like the src Element. We get also cache all the data related to the
        * @return void
        * @static
        * @method startDrag
       */
        ddCol.startDrag = function () {
          var proxyEl  = this.getDragEl(),
            srcEl = this.getEl();
          // Make the proxy look like the source element
          Dom.setStyle(srcEl, "visibility", "hidden");
          proxyEl.innerHTML = "<table><thead>" + srcEl.innerHTML
              + "</thead></table>";
        };
        /**
        * Once we end dragging a row, we swap the proxy with the real element.
        * @param x : The x Coordinate
        * @param y : The y Coordinate
        * @return void
        * @static
        * @method endDrag
        */
        ddCol.endDrag = function (x, y) {
          var proxyEl  = this.getDragEl(),
            srcEl = this.getEl();
          Dom.setStyle(proxyEl, "visibility", "hidden");
          Dom.setStyle(srcEl, "visibility", "");
          var destEl = Dom.get(id);
        };
        /*
        * This is the function that does the trick of swapping one row with another.
        * @param e : The drag event
        * @param id : The id of the row being dragged
        * @return void
        * @static
        * @method onDragOver
        */
        ddCol.onDragOver = function (e, id) {
          // Reorder rows as user drags
          return
          var destEl = Dom.get(id),
            destIndex = destEl.sectionRowIndex;
          if (destEl.nodeName.toLowerCase() === "th") {
            if (tmpIndex !== null) {
              myDataTable.deleteRow(tmpIndex);
            }
            if (tmpIndex === null) {
              myDataTable.deleteRow(srcIndex);
            }
            myDataTable.addRow(srcData, destIndex);
            tmpIndex = destIndex;
            DDM.refreshCache();
          }
        };
      };
    // Fires when the column is double clicked
    myDataTable.subscribe("theadCellClickEvent", onColumnSelect);
    //myDataTable.subscribe('cellMousedownEvent', onColumnSelect);
    //////////////////////////////////////////////////////////////////////////////
    // Create DDTarget instances when DataTable is initialized
    //////////////////////////////////////////////////////////////////////////////
    myDataTable.subscribe("initEvent", function () {
      var i, id,
        allRows = this.getTbodyEl().rows;
      for (i = 0; i < allRows.length; i++) {
        id = allRows[i].id;
        // Clean up any existing Drag instances
        if (myDTDTargets[id]) {
          myDTDTargets[id].unreg();
          delete myDTDTargets[id];
        }
        // Create a Drag instance for each row
        myDTDTargets[id] = new YAHOO.util.DDTarget(id);
      }
    });
  }());
});
