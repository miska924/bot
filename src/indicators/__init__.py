import pandas as pd

class Indicator:
    def __init__(self):
        pass
    
    def calculate(self, data: pd.DataFrame, **kwargs):
        raise NotImplementedError
    
class Divide(Indicator):
    def __init__(self):
        pass