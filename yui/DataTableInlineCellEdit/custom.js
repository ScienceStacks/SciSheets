YAHOO.util.Event.addListener(window, "load", function() {
  YAHOO.example.InlineCellEditing = function() {
    // Custom formatter for "address" column to preserve line breaks
    var formatAddress = function(elCell, oRecord, oColumn, oData) {
      elCell.innerHTML = "<pre class=\"address\">" + YAHOO.lang.escapeHTML(oData) + "</pre>";
    };

    var myColumnDefs = [
      {key:"uneditable"},
      {key:"address", formatter:formatAddress, editor: new YAHOO.widget.TextareaCellEditor()},
      {key:"city", formatter:"text", editor: new YAHOO.widget.TextboxCellEditor({disableBtns:true})},
      {key:"state", editor: new YAHOO.widget.DropdownCellEditor({dropdownOptions:YAHOO.example.Data.stateAbbrs,disableBtns:true})},
      {key:"amount", editor: new YAHOO.widget.TextboxCellEditor({validator:YAHOO.widget.DataTable.validateNumber})},
      {key:"active", editor: new YAHOO.widget.RadioCellEditor({radioOptions:["yes","no","maybe"],disableBtns:true})},
      {key:"colors", editor: new YAHOO.widget.CheckboxCellEditor({checkboxOptions:["red","yellow","blue"]})},
      {key:"fruit", editor: new YAHOO.widget.DropdownCellEditor({multiple:true,dropdownOptions:["apple","banana","cherry"]})},
      {key:"last_login", formatter:YAHOO.widget.DataTable.formatDate, editor: new YAHOO.widget.DateCellEditor()}
    ];

    var myDataSource = new YAHOO.util.DataSource(YAHOO.example.Data.addresses);
    myDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
    myDataSource.responseSchema = {
         fields: ["address","city","state","amount","active","colors","fruit",{key:"last_login",parser:"date"}]
    };

    var myDataTable = new YAHOO.widget.DataTable("cellediting", myColumnDefs, myDataSource, {});

    // Set up editing flow
    var highlightEditableCell = function(oArgs) {
      var elCell = oArgs.target;
      if(YAHOO.util.Dom.hasClass(elCell, "yui-dt-editable")) {
        this.highlightCell(elCell);
        }
    };
    myDataTable.subscribe("cellMouseoverEvent", highlightEditableCell);
    myDataTable.subscribe("cellMouseoutEvent", myDataTable.onEventUnhighlightCell);
    myDataTable.subscribe("cellClickEvent", myDataTable.onEventShowCellEditor);
    
    return {
      oDS: myDataSource,
      oDT: myDataTable
    };
  }();
});
