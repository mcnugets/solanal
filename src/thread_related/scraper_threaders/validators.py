from src.data.llm_model import gmgn_data, gmgn_main_data, holders_data, PumpfunData
from typing import Dict, List
from .Ithreader import Idata_validator  # Fixed relative import


class gmgm_validator(Idata_validator):
    def validate(self, data: Dict):
        valid_data = gmgn_data(**data)
        return valid_data


class pumpfun_validator(Idata_validator):
    def validate(self, data: Dict):
        valid_data = PumpfunData(**data)
        return valid_data


class gmgn_two_validator(Idata_validator):
    def validate(self, data: Dict):
        valid_data = gmgn_main_data(**data)
        return valid_data


class holders_validator(Idata_validator):
    def validate(self, data: Dict):
        valid_data = holders_data(**data)
        return valid_data
