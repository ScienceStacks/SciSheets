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
        "15"
      ],
      "_formula": null,
      "_name": "row"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        77,
        70,
        80,
        75,
        73,
        79,
        71,
        71,
        87,
        86,
        90,
        70,
        87,
        70,
        82
      ],
      "_formula": "# Reference Gene C(t) 1\nimport random\nsample_size = 15\nRGC_1 = [random.randint(70, 90) for x in range(sample_size)]",
      "_name": "RGC_1"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        81,
        80,
        80,
        76,
        75,
        84,
        88,
        87,
        82,
        77,
        90,
        83,
        85,
        82,
        81
      ],
      "_formula": "# Reference Gene C(t) 2\nimport random\nRGC_2 = [random.randint(70, 90) for x in range(sample_size)]",
      "_name": "RGC_2"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        81,
        88,
        80,
        98,
        87,
        88,
        92,
        98,
        95,
        80,
        92,
        92,
        96,
        95,
        89
      ],
      "_formula": "# Target Gene C(t)\nimport random\nTGC = [random.randint(80, 100) for x in range(sample_size)]",
      "_name": "TGC"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        75.67,
        75.67,
        76.33,
        88.0,
        79.67,
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
      "_formula": "# Mean of censored data for RGC 1\nmeans, _ = ProcessEff(RGC_1)\nMRGC_1 = s.coerceValues('MRGC_1', means) ",
      "_name": "MRGC_1"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        80.33,
        78.33,
        85.67,
        83.33,
        82.67,
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
      "_formula": "# Mean of censored data for MRGC_2\nmeans, _ = ProcessEff(RGC_2)\nMRGC_2 = s.coerceValues('MRGC_2', means)",
      "_name": "MRGC_2"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        83.0,
        91.0,
        95.0,
        88.0,
        93.33,
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
      "_formula": "# Mean of censored data for TGC\nMTGC, _ = ProcessEff(TGC)",
      "_name": "MTGC"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        [
          0.006215,
          2.4e-05
        ],
        [
          2e-06,
          1.0
        ],
        [
          7.7e-05,
          0.157127
        ],
        [
          0.000153,
          0.001554
        ],
        [
          0.039282,
          0.000618
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
        null
      ],
      "_formula": "# Relative cycle time of Tgt gene compared with ref 1\nrelCt_1 = np.round(2**(MRGC_1 - MTGC),6)\nrelCt_2 = np.round(2**(MRGC_2 - MTGC),6)\nrelCt = [list(relCt_1), list(relCt_2)]\nrelCt = np.reshape(relCt, [len(relCt_1), 2])",
      "_name": "relCt"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.0031,
        0.5,
        0.0786,
        0.0009,
        0.0199,
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
      "_formula": "[round(np.average(d),4) for d in relCt]",
      "_name": "netRelCt"
    }
  ],
  "_epilogue_formula": "",
  "_filepath": null,
  "_hidden_columns": [],
  "_is_evaluate_formulas": true,
  "_name": "ExpressionAnalysis",
  "_prologue_formula": ""
}