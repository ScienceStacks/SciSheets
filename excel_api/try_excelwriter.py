import pandas as pd

filename = 'pandas_simple.xlsx'
values = [10, 20, 30, 20, 15, 30, 45]

# Create a Pandas dataframe from some data.
df = pd.DataFrame({'Data': values})

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(filename, engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Sheet1', index=False)

# Close the Pandas Excel writer and output the Excel file.
writer.save()


# Using xlswriter directly
import xlsxwriter

workbook   = xlsxwriter.Workbook('filename1.xlsx')

worksheet1 = workbook.add_worksheet()
worksheet2 = workbook.add_worksheet()

for x in range(10):
  cell = "A%d" % x
  worksheet1.write(cell, x)

workbook.close()

# Reading the excel file
read_filename = "RawData.xlsx"
read_filename = "filename.xlsx"
x = pd.ExcelFile(read_filename)
df = pd.read_excel(read_filename)
import pdb; pdb.set_trace()
