from typing import Dict
import pandas as pd
import os


class RoutesReader:
    def __init__(self):
        self.dirpath = os.path.dirname(os.path.realpath(__file__))

    def read_excel(self, filepath: str = None) -> Dict[str, Dict]:
        # Check if excel filepath is specified
        if filepath is None:
            # Import excel file from routeRecords.xlsx
            filepath = os.path.join(self.dirpath, 'routeRecords.xlsx')

        # dictionary with values as list
        # use sheet_Name = [0,'Bus']
        df = pd.read_excel(filepath, sheet_name='Bus')
        output = df.set_index('Service Route').T.to_dict('dict')
        return output


def main():
    routes_reader = RoutesReader()
    print(routes_reader.read_excel())


if __name__ == '__main__':
    main()
