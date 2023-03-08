from typing import Dict
import pandas as pd
import os


class RoutesReader:
    def __init__(self):
        self.dirpath = os.path.dirname(os.path.realpath(__file__))

    def read_excel(self, relpath: str) -> Dict[str, Dict]:
        assert len(relpath)
        filepath = os.path.join(self.dirpath, relpath)

        # dictionary with values as list
        # use sheet_Name = [0,'Bus']
        df = pd.read_excel(filepath, sheet_name='Bus')
        output = df.set_index('Service Route').T.to_dict('dict')
        return output


def main():
    routes_reader = RoutesReader()
    print(routes_reader.read_excel('routeRecords.xlsx'))


if __name__ == '__main__':
    main()
