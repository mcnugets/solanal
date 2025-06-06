"""
Solana Meme Coin Analysis System using Local LLM
==============================================

This module provides an analytical pipeline for Solana meme coins using a local LLM (Language Learning Model).
It processes token data, holder information, and market metrics to generate detailed trading insights.

Key Components:
-------------
- LLM Analysis: Uses Ollama for local LLM processing
- Data Processing: Handles multiple data sources (token data, holder info)
- Structured Output: Generates organized analysis with rankings and metrics

Main Features:
------------
1. Multi-source data integration
2. Quantitative metrics calculation
3. Holder pattern analysis
4. Trend prediction
5. Risk assessment
6. Success probability estimation

Usage:
-----
```python
data_processor = llm_data_processor(files, batch_size=10)
analyser = llm_analyser(model="deepseek-r1:7b", llm_data_processor=data_processor)
for analysis in analyser.analyse():
    print(analysis)
```

Dependencies:
-----------
- ollama: For LLM operations
- pandas: For data manipulation
- logging: For operation tracking
- pathlib: For file path handling
"""

# TODO: we can expand the logic of the analysis, to integrate additional statistical
# models to output more accurate analysis
from .LLM_data_processor import llm_data_processor
import os
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any
import ollama  # Ensure you have installed the Ollama Python library
from typing import Optional, List, Dict
import json
from src import ScraperLogger as logger
from src import valid_data
from collections import deque


class llm_analyser:
    def __init__(
        self,
        model: str,
        logger: logger,
        llm_data_processor: llm_data_processor,
        batch_size: int,
    ):
        self.model = model
        self.ldp = llm_data_processor
        self.logger = logger
        """
        possibly would requier in the future for batch processsing
        """
        # self.deque = deque
        # self.deque = deque(maxlen=10)
        self.conversation_history = []
        self.temp_conversation_history = []
        self.assistant_input = None
        self.batch_size = batch_size

    # if "token_data" in data.keys():
    #     print(f"Address: {data['token_data'].get('full_address')}")

    # if "more_token_data" in data.keys():
    #     print("\nAdditional Token Info:")
    #     print(pd.DataFrame([data["more_token_data"]]).T)

    # if data["holders"]:
    #     print(f"\nHolders Info: {len(data['holders'])} holders found")

    def analyse(self, data):
        if not data:
            raise ValueError("Ting is None which means no data")

        try:
            processed_data = self.ldp.process_data(data)
            prompt = self.user_prompt(processed_data)
            _input = self.complete_prompt(
                prompt, self.assistant_input, self.conversation_history
            )
     

            self.save_analysis(_input, batched_data=self.batch_size)
            self.logger.log_info("Sending prompt to LLM model...")
            print("Sending prompt to LLM model...")

            response = ollama.chat(model=self.model, messages=_input)
            analysis = response.message
            msg_arr = analysis.content.split("</think>")
            msg = msg_arr[1]
            self.assistant_input = msg

            self.logger.log_info("Analysis received successfully")
            self.logger.log_info(response.done_reason)
            self.logger.log_info(f"Eval count:{response.eval_count}")
            self.logger.log_info(f"Eval dur:{response.eval_duration}")
            self.logger.log_info(f"Eval prompt count:{response.prompt_eval_count}")
            self.logger.log_info(f"Eval prompt dur:{response.prompt_eval_duration}")

            return msg
        except Exception as e:
            self.logger.log_error(f"LLM analysis() in LLM_processor error: {e}")
            raise RuntimeError(f"Error in LLM analysis(): {str(e)}")

    def save_analysis(self, last_added_data, batched_data):
        try:
            self.temp_conversation_history.append(last_added_data)
            if len(self.temp_conversation_history) == batched_data:
                saved_batch = pd.DataFrame(self.temp_conversation_history)
                check_file = Path("conversation_history.json")
                new_batches = saved_batch

                if check_file.exists():
                    try:
                        if check_file.stat().st_size>0:
                            get_saved_batches = pd.read_json(check_file)
                        else:
                            get_saved_batches = pd.DataFrame()
                        
                     
                        new_batches = pd.concat(
                            [get_saved_batches, saved_batch], ignore_index=True
                        )
                    except pd.errors.EmptyDataError:
                        logging.error("JSON file is empty")
                        return
                
                    except ValueError as e:
                        logging.error(f"Error reading JSON file: {e}")
                        return
                 
                
                try:
                    self.temp_conversation_history.clear()
                    new_batches.to_json(check_file, indent=4)
                except IOError as e:
                    logging.error(f"Error saving to JSON file: {e}")

        except Exception as e:
            logging.error(f"Unexpected error in save_analysis: {e}")

    def complete_prompt(
        self, user_prompt: Dict, assistant_prompt, conversation_h: List
    ) -> List[Dict]:

        try:

            if not conversation_h:
                conversation_h.append(self.system_prompt())

            if assistant_prompt:
                assistant = {"role": "assistant", "content": assistant_prompt}
                conversation_h.append(assistant)

            conversation_h.append(user_prompt)

            return conversation_h

        except (TypeError, ValueError) as e:
            logging.error(f"Error in complete_prompt: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in complete_prompt: {str(e)}")
            raise

    def system_prompt(self) -> Dict:
        system_prompt = """
                        You are a pragmatic, objective, quant/data analyst of the crypto trading market.\n\n
                        You need to give an unbiased prediction.
                        """
        return {"role": "system", "content": system_prompt}

    def user_prompt(self, data: str) -> Dict:

        user_prompt = f"""
                  
                    Solana Meme Coin Analysis Data:
                    **NOTE**: 3 days of holding max. Recommend holding duration in this timeframe from minutes to days.
                    
                    **Input Data:**
                    {data}


                    Instructions:

                    1.  Calculate quantitative metrics (volatility, liquidity, growth, holder concentration) for each coin.
                    2.  Objectively compare and rank coins based on these metrics, prioritizing: High Growth, Moderate Volatility, Good Liquidity, Decentralized Holders.
                    3.  Analyze holder data for patterns: new holder increase, whale accumulation, correlation of holder activity with price changes.
                    4.  Evaluate trend likelihood for each coin within 1 week, justifying with data and patterns.
                    5.  Estimate optimal holding duration (within 1 week) for each promising coin, justifying with data (e.g., volatility).
                    6.  Provide probability of success rate (e.g., High/Medium/Low or %) for each coin achieving positive returns (define "success", e.g., 10%+ price increase), justifying your estimate.
                    7.  Assess early-stage meme coin potential for ATH, considering: community engagement (if data available), meme/narrative strength, uniqueness, early holder indicators.

                    Output Format:

                    Present a structured and organized analysis including:

                    * Coin Ranking Table: Rank coins by potential, include key metrics and justifications.
                    * Individual Coin Analysis Sections: For each coin, provide:
                        * Summary of Key Metrics and Patterns.
                        * Trend Likelihood Evaluation (with justification).
                        * Optimal Holding Duration (with justification).
                        * Probability of Success Rate (with justification and definition of success).
                        * ATH Potential Analysis.

                    Emphasis:  Provide data-driven, objective analysis with clear justifications. Avoid vague statements and focus on actionable, data-based insights. Be short and concise
                    """
        return {"role": "user", "content": user_prompt}


# TODO: i need to add the list of insiders, wallets i follow and whales
# for now i will hardcode it but ill need amore sophisticated way of doing this
if __name__ == "__main__":

    try:
        # Set up logging
        logging.basicConfig(level=logging.INFO)

        # Determine the project root directory (adjust levels as needed)
        base_path = Path(__file__).resolve().parent.parent.parent

        # Define file paths for CSVs and holders directory
        files = {
            "token_data": str(base_path / "pumpfun_data.csv"),
            "more_token_data": str(base_path / "gmgn_data.csv"),
            "holders": str(base_path / "holders"),
        }

        # Initialize the data processor with a chosen batch size (e.g., 10)
        data_processor = llm_data_processor(files, batch_size=10)

        # Specify your model name for ollama (update with your actual model identifier)
        model_name = "deepseek-r1:7b"

        # Initialize the LLM analyser with the model and data processor
        analyser = llm_analyser(model=model_name, llm_data_processor=data_processor)

        # Run analysis for each data record and print the results
        for analysis in analyser.analyse():
            print("\n==== Analysis ====")
            print(analysis)
            print("-" * 50)

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
