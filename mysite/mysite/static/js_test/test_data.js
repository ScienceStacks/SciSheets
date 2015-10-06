

/* ----------- Code customized for data --------------*/
var myColumnDefs, newDataSource, columnNames, tableId, tableCaption,
  myDataTable, highlightEditableCell, myDataSource, id, tableElement,
  captionElement, sciSheets;
sciSheets = new SciSheets();
tableId = "cellediting";
tableCaption = "New table";
columnNames = ["row", "name", "address", "salary"];
myColumnDefs = [
  {key: "row", formatter: sciSheets.formatColumn("row"), editor:  new YAHOO.widget.TextareaCellEditor()},
  {key: "name", formatter: sciSheets.formatColumn("name"), editor:  new YAHOO.widget.TextareaCellEditor()},
  {key: "address", formatter: sciSheets.formatColumn("address"), editor:  new YAHOO.widget.TextareaCellEditor()},
  {key: "salary", formatter: sciSheets.formatColumn("salary"), editor:  new YAHOO.widget.TextareaCellEditor()}
];
newDataSource = [
  {row: "1", name: "John A. Smith", address: "1236 Some Street", salary: "12.33"},
  {row: "2", name: "Joan B. Jones", address: "3271 Another Ave", salary: "34556"},
  {row: "3", name: "Bob C. Uncle", address: "9996 Random Road", salary: "893"},
  {row: "4", name: "John D. Smith", address: "1623 Some Street", salary: "0.092"},
  {row: "5", name: "Joan E. Jones", address: "3217 Another Ave", salary: "23456"}
];
