from typing import Dict, List
from src import valid_data, gmgn_main_data, gmgn_data, holders_data


class token_data_validator:
    def __init__(self, logger):
        self.logger = logger

    def validate(self, data: Dict[str, List | Dict]) -> valid_data:
        try:
            
            if "gmgn_2" in data:
                main = self.validate_pumpfun(data['gmgn_2'])
            else:
                main = self.validate_pumfun(data['pumpfun'])
            gmgn_data = self.validate_gmgn(data["gmgn"]) if "gmgn" in data else None
            holders = self.validate_holders(data["holders"]) if "holders" in data else None
            dict_data = {
                "main": main,
                "gmgn_data_": gmgn_data,
                "holders": holders,
            }
            data = valid_data(**dict_data)
            self.logger.log_info(f'the data was validated  {data}')
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
