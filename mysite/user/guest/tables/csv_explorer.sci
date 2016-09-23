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
        ".",
        "",
        "nan",
        "nan",
        "nan",
        "nan"
      ],
      "_formula": null,
      "_name": "Path"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        "Glu.csv",
        "LL-DAP.csv",
        "THDPA.csv",
        null,
        null,
        null
      ],
      "_formula": null,
      "_name": "CSVFiles"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        "Glu.csv",
        "",
        null,
        null,
        null,
        null
      ],
      "_formula": null,
      "_name": "InputFile"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.2,
        0.5,
        2.0,
        5.0,
        10.0,
        NaN
      ],
      "_formula": null,
      "_name": "S"
    },
    {
      "SciSheets_Class": "<class 'scisheets.core.column.Column'>",
      "_asis": false,
      "_cells": [
        0.02,
        0.08,
        0.11,
        0.2,
        0.3
      ],
      "_formula": null,
      "_name": "V"
    }
  ],
  "_epilogue_formula": "# Prologue\nimport numpy as np\nfrom os import listdir\nfrom os.path import isfile, join\n\npath = param(s, 'Path')\nInputFile[2] = \"h\"\nCSVFiles = [f for f in listdir(path) if f[-4:] == '.csv']\nCSVFiles.sort()\n\nnames = s.getColumnNames()\npath = param(s, 'Path')\n# Delete old columns\nfor name in names:\n  if not name in ['row', 'InputFile', 'CSVFiles', 'Path']:\n    s.deleteColumn(name)\n# Get the file to process\nthis_file = InputFile[0]\n# Check for a missing file\nInputFile[2] = \"h\"\nif len(this_file) > 0:\n  if not this_file in CSVFiles:\n    InputFile[1] = \"***File\"\n  else:\n    InputFile[1] = None\n    full_file = join(path, this_file)\n    new_columns = importCSV(s, full_file)",
  "_filepath": "/home/ubuntu/SciSheets/mysite/user/guest/tables/csv_explorer.pcl",
  "_hidden_columns": [],
  "_is_evaluate_formulas": true,
  "_name": "CSVExplorer",
  "_prologue_formula": "# Prologue\nimport numpy as np\nfrom os import listdir\nfrom os.path import isfile, join\n\npath = param(s, 'Path')\nInputFile[2] = \"h\"\nCSVFiles = [f for f in listdir(path) if f[-4:] == '.csv']\nCSVFiles.sort()\n\nnames = s.getColumnNames()\npath = param(s, 'Path')\n# Delete old columns\nfor name in names:\n  if not name in ['row', 'InputFile', 'CSVFiles', 'Path']:\n    s.deleteColumn(name)\n# Get the file to process\nthis_file = InputFile[0]\n# Check for a missing file\nInputFile[2] = \"h\"\nif len(this_file) > 0:\n  if not this_file in CSVFiles:\n    InputFile[1] = \"***File\"\n  else:\n    InputFile[1] = None\n    full_file = join(path, this_file)\n    new_columns = importCSV(s, full_file)"
}