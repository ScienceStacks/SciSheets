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
        "6"
      ],
      "_formula": null,
      "_name": "row"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        "Glu.csv",
        "THDPA.csv",
        "LL-DAP.csv",
        null,
        null,
        null
      ],
      "_formula": "[x for x in listdir(\".\") if x[-4:] == \".csv\"]",
      "_name": "FileList"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        "THDPA.csv",
        "nan",
        "nan",
        "nan",
        "nan",
        "nan"
      ],
      "_formula": null,
      "_name": "CSVFile"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.01,
        0.05,
        0.12,
        0.2,
        0.5,
        1.0
      ],
      "_formula": "csv_file =CSVFile[0]\ndf = pd.read_csv(csv_file)\nS = df['S']\nV = df['V']",
      "_name": "S"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.11,
        0.19,
        0.21,
        0.22,
        0.21,
        0.24
      ],
      "_formula": null,
      "_name": "V"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        100.0,
        20.0,
        8.333333333333334,
        5.0,
        2.0,
        1.0
      ],
      "_formula": "1/S",
      "_name": "INV_S"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        9.090909090909092,
        5.2631578947368425,
        4.761904761904762,
        4.545454545454546,
        4.761904761904762,
        4.166666666666667
      ],
      "_formula": "1/V",
      "_name": "INV_V"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        4.357398728502525,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN
      ],
      "_formula": "intercept(INV_S,INV_V)",
      "_name": "INTERCEPT"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.04727827885497449,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN
      ],
      "_formula": "slope(INV_S, INV_V)",
      "_name": "SLOPE"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.2294947197415791,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN
      ],
      "_formula": "1/INTERCEPT",
      "_name": "V_MAX"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.010850115355686595,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN
      ],
      "_formula": "SLOPE*V_MAX",
      "_name": "K_M"
    }
  ],
  "_epilogue_formula": "",
  "_filepath": "/home/ubuntu/SciSheets/mysite/user/guest/tables/mechaelis_menton.pcl",
  "_hidden_columns": [],
  "_is_evaluate_formulas": true,
  "_name": "MechaelisMenton",
  "_prologue_formula": ""
}