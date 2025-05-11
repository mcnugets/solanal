from typing import Optional, Dict, List
import re

from src.core.logger import ScraperLogger as log
from colorama import init, Fore, Back, Style

init()

CLEANING_PATTERNS_g = {
    r"\n+": "#",  # Replace newlines with hash
    r"#+": "#",  # Normalize multiple hashes
    r"^\#|\#$": "",  # Remove leading/trailing hashes
    r"(.)\1+": r"\1",
}


class TextProcessor:
    def __init__(
        self, logger: log, patterns: List, CLEANING_PATTERNS: Dict = CLEANING_PATTERNS_g
    ):
        self.patterns = self.setup_reg(patterns=patterns)
        self.logger = logger
        self.CLEANING_PATTERNS = CLEANING_PATTERNS
        self.regex_patterns = {
            re.compile(pattern): repl
            for pattern, repl in self.CLEANING_PATTERNS.items()
        }

    # def s(self, item):

    def setup_reg(self, patterns):
        esc = [re.escape(i) for i in patterns]
        pattern_ = re.compile(r"(?<!\S)(?:" + "|".join(esc) + r")(?!\S)")

        print(f" the indicators  {pattern_}")
        return pattern_

    def clean_indicators(self, raw_data: str) -> str:
        cleaned = self.patterns.sub("", raw_data)
        return cleaned

    def split_text(self, text: str) -> Optional[List[str]]:
        try:
            splitted_text = text.split("#")
            tokens: List[str] = []
            i = 0
            # 2) walk through raw_tokens and merge digit/slash/digit
            while i < len(splitted_text):
                tok = splitted_text[i].strip()
                # merge slash between digits (e.g. '4','/','8' → '4/8')
                if tok == "/" and tokens and i + 1 < len(splitted_text):
                    prev = tokens[-1]
                    nxt = splitted_text[i + 1].strip()
                    if re.fullmatch(r"\d+", prev) and re.fullmatch(r"\d+", nxt):
                        tokens[-1] = f"{prev}/{nxt}"
                        i += 2
                        continue

                # skip empties and lone '>'
                if tok and tok != ">":
                    tokens.append(tok)
                i += 1
            splitted_text = tokens
            # print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")
            # print(f"{Fore.MAGENTA}SPLIT DONE: {splitted_text}{Style.RESET_ALL}")
            # print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")
            return splitted_text
        except Exception as e:
            print(f"Split error: {e}")
            return None

    def clean_text(self, raw_data: str) -> Optional[str]:
        try:
            block = self.clean_indicators(raw_data)
            # print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")
            self.logger.log_info(f"CLEANED THE RAW: {block}")
            # print(f"{Fore.YELLOW}INDICATORS CLEANED: {block}{Style.RESET_ALL}")
            # print(f"{Fore.CYAN}---------------------{Style.RESET_ALL}")
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


# CHROME\nCHROME\n0%\nRun\n4E35w...yBc\nName\nCA\n$0.0\u208542131\n24h\n-13.94%\nSnipers\n>\n4\n/\n8\nBlueChip\n>\n0%\nTop 10\n5.8%\nAudit\n>\nSafe\n4/4\nTaxes\nDex\n1%#4E35wqoubSGPJGyubeLM9kimxsoxDnNaKZRdw9LS7yBc
def main():
    import re

    # Dummy logger with a log_info method
    class SimpleLogger:
        def log_info(self, msg):
            print(f"[LOG] {msg}")

    logger = SimpleLogger()

    # Compile a pattern to strip out newline characters
    patterns = [
        "24h",
        "Snipers",
        "BlueChip",
        "Name",
        "CA",
        "Top 10",
        "Audit",
        ">",
        "Safe",
        "Share",
        "Taxes",
        "Dex",
    ]
    patterns_2 = [
        "Liq",
        "Vol",
        "?",
        "V",
        "MC",
    ]
    # No extra regex replacements for this test
    cleaning_pat = CLEANING_PATTERNS_g

    # Instantiate the TextProcessor
    tp = TextProcessor(logger=logger, patterns=patterns, CLEANING_PATTERNS=cleaning_pat)

    # Sample raw data containing newlines and a '#' split marker
    raw_data = " CHROME\nCHROME\n0%\nRun\n4E35w...yBc\nName\nCA\n$0.0\u208542131\n24h\n-13.94%\nSnipers\n>\n4\n/\n8\nBlueChip\n>\n0%\nTop 10\n5.8%\nAudit\n>\nSafe\n4/4\nTaxes\nDex\n1%#4E35wqoubSGPJGyubeLM9kimxsoxDnNaKZRdw9LS7yBc"
    like_it_raw = "EdgeCoin\nMicroSoft Edge Secret Coin\nBuy\n3s\n7cbJG...k8T\nLiq\n$2.34\n0\nV\n$0\nMC\n$0#7cbJGkeEVRH5BjVgA8MLAdpM5K8Gtizftri9q8fm9k8T"
    print("Raw data:", raw_data)

    # Run processing
    result = tp.process(raw_data)
    print("Processed result:", result)


if __name__ == "__main__":
    main()
