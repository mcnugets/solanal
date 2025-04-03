from typing import Dict, List
from src import valid_data, gmgn_main_data, gmgn_data, holders_data


class token_data_validator:
    def __init__(self, logger):
        self.logger = logger

    def validate(self, data: Dict[str, List | Dict]) -> valid_data:
        try:
            gmgn_main = self.validate_pumpfun(data["pumpfun"])
            gmgn_data = self.validate_gmgn(data["gmgn"])
            holders = self.validate_holders(data["holders"])
            dict_data = {
                "pumpfun_data": gmgn_main,
                "gmgn_data": gmgn_data,
                "holders": holders,
            }
            data = valid_data(**dict_data)
            return data
        except Exception as e:
            self.logger.log_error(error_msg=f"Error validating data:", exc_info=e)
            print(f"Error validating data: {e}")
            return None

    def validate_holders(self, data):
        return holders_data(**data)

    def validate_gmgn(self, data):
        return gmgn_data(**data)

    def validate_pumpfun(self, data):
        return gmgn_main_data(**data)
