from typing import Dict, Any
import pandas as pd
import os


class RoutesReader:
    def __init__(self):
        self.dirpath = os.path.dirname(os.path.realpath(__file__))

    def read_excel(self, relpath: str) -> Dict[Any, Dict]:
        assert len(relpath)
        filepath = os.path.join(self.dirpath, relpath)

        # dictionary with values as list
        # use sheet_Name = [0,'Bus']
        buses = pd.ExcelFile(filepath).sheet_names
        output = {}
        for i in buses:
            df = pd.read_excel(filepath, sheet_name=i)
            df = df[df["GPS Location"] != "No bus stop, ignore"]
            df = df[df["GPS Location"] != "no bus stop (ignore)"]
            output[i] = df.set_index('Stop ID')
        return output
