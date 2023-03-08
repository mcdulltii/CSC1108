import pandas as pd

# dictionary with values as list
# use sheet_Name = [0,'Bus']
df = pd.read_excel('routeRecords.xlsx', sheet_name='Bus')
output = df.set_index('Service Route').T.to_dict('dict')

print(output)