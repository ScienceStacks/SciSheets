{
  "SciSheets_Class": "<class 'scisheets.ui.dt_table.DTTable'>",
  "_columns": [
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": true,
      "_cells": [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18"
      ],
      "_formula": null,
      "_name": "row"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        4.0,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN
      ],
      "_formula": null,
      "_name": "Ncol"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.0,
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
        11.0,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN
      ],
      "_formula": "ncol = int(Ncol[0])\nnrow = 3\nData = range(nrow*ncol)",
      "_name": "Data"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        [
          0,
          1,
          2
        ],
        [
          3,
          4,
          5
        ],
        [
          6,
          7,
          8
        ],
        [
          9,
          10,
          11
        ],
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null
      ],
      "_formula": "np.reshape(Data, [ncol, nrow])",
      "_name": "RestructuredData"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        1.0,
        4.0,
        7.0,
        10.0,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN
      ],
      "_formula": "Col_3 = []\nAverages = []\nfor x in RestructuredData:\n  Averages.append(np.average(x))\n",
      "_name": "Averages"
    }
  ],
  "_epilogue_formula": "",
  "_filepath": null,
  "_hidden_columns": [],
  "_is_evaluate_formulas": true,
  "_name": "StructuredData",
  "_prologue_formula": ""
}