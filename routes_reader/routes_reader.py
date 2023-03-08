import pandas as pd
import os


class RoutesReader:
    def __init__(self, filepath=None):
        # Check if excel filepath is specified
        if filepath is None:
            # Import excel file from routesRecords.xlsx
            dirpath = os.path.dirname(os.path.realpath(__file__))
            self.filepath = os.path.join(dirpath, 'routeRecords.xlsx')
        else:
            self.filepath = filepath
        assert self.filepath is not None

    def read_excel(self):
        # dictionary with values as list
        # use sheet_Name = [0,'Bus']
        df = pd.read_excel(self.filepath, sheet_name='Bus')
        output = df.set_index('Service Route').T.to_dict('dict')
        return output


def main():
    routes_reader = RoutesReader()
    print(routes_reader.read_excel())


if __name__ == '__main__':
    main()
