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
        0.01,
        0.05,
        0.12,
        0.2,
        0.5,
        1.0
      ],
      "_formula": null,
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
        8.33,
        5.0,
        2.0,
        1.0
      ],
      "_formula": "INV_S = 1/S\nINV_S = roundValues(INV_S,2)",
      "_name": "INV_S"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        9.09,
        5.26,
        4.76,
        4.55,
        4.76,
        4.17
      ],
      "_formula": "roundValues(1/V,2)",
      "_name": "INV_V"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        4.358,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN
      ],
      "_formula": "roundValues(intercept(INV_S,INV_V),3)",
      "_name": "INTERCEPT"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.047,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN
      ],
      "_formula": "roundValues(slope(INV_S, INV_V),3)",
      "_name": "SLOPE"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.229,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN
      ],
      "_formula": "roundValues(1/INTERCEPT,3)",
      "_name": "V_MAX"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.011,
        NaN,
        NaN,
        NaN,
        NaN,
        NaN
      ],
      "_formula": "roundValues(SLOPE*V_MAX,3)",
      "_name": "K_M"
    }
  ],
  "_epilogue_formula": "# Prologue\nimport math as mt\nimport numpy as np\nfrom os import listdir\nfrom os.path import isfile, join\nimport pandas as pd\nimport scipy as sp\nfrom numpy import nan  # Must follow sympy import\n",
  "_filepath": "/home/ubuntu/SciSheets/mysite/user/guest/tables/mechaelis_menten_demo.sci",
  "_hidden_columns": [],
  "_is_evaluate_formulas": true,
  "_name": "MechaelisMenton",
  "_prologue_formula": "# Prologue\nimport math as mt\nimport numpy as np\nfrom os import listdir\nfrom os.path import isfile, join\nimport pandas as pd\nimport scipy as sp\nfrom numpy import nan  # Must follow sympy import\n"
}