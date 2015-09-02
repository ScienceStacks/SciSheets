var YUI_config={"filter":"min","maxURLLength":1024,"root":"3.18.1/","groups":{"site":{"combine":true,"comboBase":"/combo/js?","root":"","modules":{"hoverable":{"path":"hoverable-min.js","requires":["event-hover","node-base","node-event-delegate"]},"search":{"path":"search-min.js","requires":["autocomplete","autocomplete-highlighters","node-pluginhost"]},"api-filter":{"path":"apidocs/api-filter-min.js","requires":["autocomplete-base","autocomplete-highlighters","autocomplete-sources"]},"api-list":{"path":"apidocs/api-list-min.js","requires":["api-filter","api-search","event-key","node-focusmanager","tabview"]},"api-search":{"path":"apidocs/api-search-min.js","requires":["autocomplete-base","autocomplete-highlighters","autocomplete-sources","escape"]}}}}};
if (location.protocol.indexOf('https') > -1) {
  YUI_config.comboBase = 'https://yui-s.yahooapis.com/combo?';
  YUI_config.combine = true;
 }

YUI().use("datatable", function (Y) {

    // A table from data with keys that work fine as column names
    var simple = new Y.DataTable({
        columns: [{key: 'id', label: "id", editable: false},
                  {key: 'name', label: "nmme", editable: true, editor: "inlineNumber"},
                  "price"],
        data   : [
            { id: "ga_3475", name: "gadget",   price: "$6.99" },
            { id: "sp_9980", name: "sprocket", price: "$3.75" },
            { id: "wi_0650", name: "widget",   price: "$4.25" }
        ],
        summary: "Price sheet for inventory parts",
        editable: true,
        caption: "Example table with simple columns",
        defaultEditor: 'inline',
        editOpenType: 'dblclick'
    });

    simple.render("#simple");

    // Data with less user friendly field names
    var data = [
        {
            mfr_parts_database_id   : "ga_3475",
            mfr_parts_database_name : "gadget",
            mfr_parts_database_price: "$6.99"
        },
        {
            mfr_parts_database_id   : "sp_9980",
            mfr_parts_database_name : "sprocket",
            mfr_parts_database_price: "$3.75"
        },
        {
            mfr_parts_database_id   : "wi_0650",
            mfr_parts_database_name : "widget",
            mfr_parts_database_price: "$4.25"
        }
    ];

    var columnDef = [
        {
            key  : "mfr_parts_database_id",
            label: "Mfr Part ID",
            abbr : "ID"
        },
        {
            key  : "mfr_parts_database_name",
            label: "Mfr Part Name",
            abbr : "Name"
        },
        {
            key  : "mfr_parts_database_price",
            label: "Wholesale Price",
            abbr : "Price"
        }
    ];

    var withColumnLabels = new Y.DataTable({
        columns: columnDef,
        data   : data,
        summary: "Price sheet for inventory parts",
        caption: "These columns have labels and abbrs"
    }).render('#labels');

});
