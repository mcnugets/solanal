from typing import Optional, Dict, List
import re

from colorama import init, Fore, Back, Style

init()

# CLEANING_PATTERNSs = {
#     r"\n+": "#",  # Replace newlines with hash
#     r"#+": "#",  # Normalize multiple hashes
#     r"^\#|\#$": "",  # Remove leading/trailing hashes
#     r"(.)\1+": r"\1",
# }


class TextProcessor:
    def __init__(self, patterns: dict, CLEANING_PATTERNS: dict):
        self.patterns = patterns
        self.CLEANING_PATTERNS = CLEANING_PATTERNS
        self.regex_patterns = {
            re.compile(pattern): repl
            for pattern, repl in self.CLEANING_PATTERNS.items()
        }

    def clean_indicators(self, raw_data: str) -> str:
        text = raw_data
        for pattern, replacement in self.patterns.items():
            text = re.sub(pattern, replacement, text)
        return text

    def split_text(self, text: str) -> Optional[List[str]]:
        try:
            splitted_text = text.split("#")
            print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}SPLIT DONE: {splitted_text}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")
            return splitted_text
        except Exception as e:
            print(f"Split error: {e}")
            return None

    def clean_text(self, raw_data: str) -> Optional[str]:
        try:
            block = self.clean_indicators(raw_data)
            print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}INDICATORS CLEANED: {block}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")
            for pattern, replacement in self.regex_patterns.items():
                print(block)
                block = pattern.sub(replacement, block)
            return block
        except Exception as e:
            print(f"Clean error: {e}")
            return None

    def process(
        self,
        raw_data: Optional[str] = None,
    ) -> Optional[List[str]]:
        if not raw_data:
            return None

        try:
            cleaned = self.clean_text(raw_data)
            print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")
            print(f"{Fore.GREEN}CLEANED: {cleaned}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")
            if cleaned:
                return self.split_text(cleaned)
        except Exception as e:
            print(f"Process error: {e}")
        return None
