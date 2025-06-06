from src.core.logger import ScraperLogger as logger
from src.thread_related.factories.threader_factory import threader_factory
from src.llm.LLM_threading import llm_threader
from src.core.config import CONFIG, queue_m
from src.llm.token_valid import token_data_validator
log = logger()

# Define your sample compiled data here
sample_compiled_data = {
    "gmgn_2": {
        "ticker": "NODEGO",
        "name": "NODEGOAI",
        "age": "25s",
        "address": "BbaqD...mHC",
        "liquidity": "$315.4",
        "total_holders": "2",
        "volume": "$68.9K",
        "market_cap": "$1.1M",
        "top_10": "9%",
        "dev_holds": "0.5%",
        "insiders": "5",
        "snipers": "Buy",
        "rug": "7%",
        "migrated": "1",
        "full_address": "wpeori345345pump"
    },
    "holders": {
        "Account": {
            0: "SomeAccountAddress1",
            1: "SomeAccountAddress2",
            2: "SomeAccountAddress3"
        },
        "Token_Account": {
            0: "SomeTokenAccount1",
            1: "SomeTokenAccount2",
            2: "SomeTokenAccount3"
        },
        "Quantity": {
            0: 10000.5,
            1: 5000.0,
            2: 2500.75
        },
        "Percentage": {
            0: 50.0,
            1: 25.0,
            2: 12.5
        }
    }
}


# ... existing helper functions (get_holders, load_data) ...


if __name__ == "__main__":
    print("starting")
    fac = threader_factory()
    data_validation = token_data_validator(logger=log)
    validated_data = data_validation.validate(sample_compiled_data)
    print('=' * 40)
  
    queue_m.get_queue("compiled")["output_queue"].put(validated_data)
    print("validation success")
    llm_thread: llm_threader = fac.create_threader(threader_type='llm', 
    configs=CONFIG, topic="")

    llm_thread.start_all()
