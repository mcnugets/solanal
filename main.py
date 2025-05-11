import requests
import os
import math
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup


def fetch_migrated_coins_from_pumpfun():
    print("Fetching migrated coins from pump.fun...")
    url = "https://pump.fun/advanced"
    try:
        r = requests.get(url, timeout=10)
        print(r.text)
        if r.status_code != 200:
            print(f"Error: Received status code {r.status_code} from pump.fun")
            return []
        soup = BeautifulSoup(r.text, "html.parser")

        table = soup.find("table", {"class": "w-full table-fixed min-w-[1490px]"})
        migrated_coins = []
        if table:
            rows = table.find_all("tr")
            if len(rows) > 1:
                for row in rows[1:]:
                    cols = row.find_all("td")
                    if len(cols) > 2:
                        symbol = cols[0].text.strip()
                        address = cols[1].text.strip()
                        migrated_time_str = cols[2].text.strip()
                        migrated_coins.append(
                            {
                                "symbol": symbol,
                                "address": address,
                                "migrated_time": migrated_time_str,
                            }
                        )
        print(f"Found {len(migrated_coins)} migrated coins.")
        return migrated_coins
    except Exception as e:
        print(f"Exception fetching pump.fun data: {e}")
        return []


def convert_age_to_hours(age_str):
    # Safe parsing with try/except
    try:
        if "h" in age_str:
            return float(age_str.replace("h", ""))
        elif "m" in age_str:
            minutes = float(age_str.replace("m", ""))
            return minutes / 60.0
        elif "d" in age_str:
            days = float(age_str.replace("d", ""))
            return days * 24
        return 24.0
    except Exception as e:
        print(f"Exception converting age string '{age_str}': {e}")
        return 24.0


def filter_coins_on_dexscreener(coins):
    print("Filtering coins on Dexscreener...")
    filtered = []
    for c in coins:
        address = c["address"]
        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                print(f"Failed to fetch dex data for {address}: {r.status_code}")
                continue
            dex_data = r.json()
            pairs = dex_data.get("pairs", [])
            if not pairs:
                continue

            for p in pairs:
                pair_age_str = p.get("pairAge", "24h")
                pair_age_hours = convert_age_to_hours(pair_age_str)
                txns = p.get("txns", {})
                one_hour_txns = txns.get("h1", 0)
                five_min_txns = txns.get("m5", 0)

                if (
                    pair_age_hours <= 24
                    and one_hour_txns >= 150
                    and five_min_txns >= 25
                ):
                    filtered.append(c)
                    break
        except Exception as e:
            print(f"Exception filtering coin {address} on Dexscreener: {e}")
    print(f"Filtered down to {len(filtered)} coins after Dexscreener checks.")
    return filtered


def analyze_holders_gmgn(token_address):
    print(f"Analyzing holders for {token_address} on gmgn.ai...")
    url = f"https://gmgn.ai/holders?chain=sol&token={token_address}"
    holders = []
    clusters = []
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"Non-200 status from gmgn.ai holders page: {r.status_code}")
            return {"holders": [], "clusters": []}
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"id": "holders-table"})
        if table:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    addr = cols[0].text.strip()
                    supply_str = cols[1].text.strip().replace("%", "")
                    try:
                        pct = float(supply_str)
                    except:
                        pct = 0.0
                    holders.append({"address": addr, "supply_pct": pct})
    except Exception as e:
        print(f"Exception analyzing gmgn holders for {token_address}: {e}")
    return {"holders": holders, "clusters": clusters}


def analyze_clusters_bubblemaps(token_address):
    print(f"Analyzing clusters for {token_address} on bubblemaps.io...")
    url = f"https://bubblemaps.io/token/solana/{token_address}"
    clusters = []
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"Non-200 from bubblemaps: {r.status_code}")
            return {"clusters": []}
        soup = BeautifulSoup(r.text, "html.parser")
        # Placeholder parsing
    except Exception as e:
        print(f"Exception analyzing bubblemaps for {token_address}: {e}")
    return {"clusters": clusters}


def check_twitter_activity_tweetscout(token_symbol):
    print(f"Checking Twitter activity for {token_symbol} on tweetscout...")
    url = f"https://app.tweetscout.io/search?query={token_symbol}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"Non-200 from tweetscout: {r.status_code}")
            return 0
        soup = BeautifulSoup(r.text, "html.parser")
        score_span = soup.find("span", {"id": "score"})
        if score_span:
            try:
                return float(score_span.text.strip())
            except:
                pass
    except Exception as e:
        print(f"Exception checking tweetscout for {token_symbol}: {e}")
    return 0


def check_validity_solsniffer(token_address):
    print(f"Checking validity for {token_address} on solsniffer.com...")
    url = f"https://solsniffer.com/token/{token_address}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"Non-200 from solsniffer: {r.status_code}")
            return 0
        soup = BeautifulSoup(r.text, "html.parser")
        score_div = soup.find("div", class_="score")
        if score_div and "Score:" in score_div.text:
            part = score_div.text.split("Score:")[1].strip()
            try:
                return float(part)
            except:
                return 0
    except Exception as e:
        print(f"Exception checking solsniffer for {token_address}: {e}")
    return 0


def fetch_smart_degen_wallets():
    print("Fetching smart degen wallets from gmgn.ai...")
    url = "https://gmgn.ai/trade?chain=sol&tab=smart_degen"
    wallets = []
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"Non-200 from gmgn smart degens: {r.status_code}")
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"id": "smart-degen-table"})
        if table:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all("td")
                if cols:
                    addr = cols[0].text.strip()
                    wallets.append({"address": addr})
    except Exception as e:
        print(f"Exception fetching smart degens: {e}")
    return wallets


def check_smart_degen_involvement(token_address, holders, smart_degen_wallets):
    degen_addresses = {w["address"].lower() for w in smart_degen_wallets}
    involved_degens = 0
    for h in holders:
        if h.get("address", "").lower() in degen_addresses:
            involved_degens += 1
    return involved_degens


def calculate_success_rate(
    age_hours, holder_data, twitter_score, validity_score, degen_involvement
):
    score = 0
    if age_hours <= 6:
        score += 30
    elif age_hours <= 24:
        score += 20

    holders = holder_data.get("holders", [])
    if holders:
        max_pct = max(h.get("supply_pct", 0) for h in holders)
        if max_pct <= 4:
            score += 30
        else:
            score -= 20

    score += (twitter_score / 100.0) * 20

    if validity_score < 87:
        score = 0
    else:
        extra = ((validity_score - 87) / 13.0) * 20
        score += extra

    if degen_involvement > 0:
        bonus = min(degen_involvement * 5, 15)
        score += bonus

    score = min(max(score, 0), 100)
    return round(score)


def llm_refine_score_ollama(coin_info, initial_score, model="llama2"):
    print("Refining score with LLM via Ollama...")
    system_instructions = """
    You are an expert crypto analyst AI trained on historical meme coin performance data, 
    token distribution patterns, on-chain metrics, and the behavior of top 'smart degen' traders on Solana.
    You specialize in identifying early-stage meme coins with high potential for achieving all-time highs.

    You have these guidelines:
    - Younger token <6h = better
    - Validity >=87 is a must
    - Balanced distribution (no >4% holder)
    - Positive Twitter sentiment (score >50)
    - Smart Degens involved early = big bullish signal

    Your job: Refine the success rate given the data and produce a single integer (0-100).


    """

    user_info = f"""
Token details:
- Symbol: {coin_info['symbol']}
- Age (hours): {coin_info['age_hours']:.2f}
- Max Holder Supply %: {coin_info.get('max_holder_pct', 'Unknown')}
- Twitter Score (0-100): {coin_info.get('twitter_score', 0)}
- Validity Score (0-100): {coin_info.get('validity_score', 0)}
- Preliminary Heuristic Success Rate (0-100): {initial_score}
- Smart Degen Involvement: {coin_info.get('degen_involvement', 0)} wallets involved

Return ONLY the final LLM-Adjusted success rate (0-100).
"""
    prompt = system_instructions.strip() + "\n\n" + user_info.strip()
    try:
        result = subprocess.run(
            ["ollama", "run", model, "-p", prompt],
            capture_output=True,
            text=True,
            check=True,
        )
        response = result.stdout.strip()
        try:
            llm_score = int(response)
        except:
            llm_score = initial_score
        llm_score = min(max(llm_score, 0), 100)
        return llm_score
    except FileNotFoundError:
        print("Ollama is not installed or not in PATH. Returning initial score.")
        return initial_score
    except subprocess.CalledProcessError as e:
        print(f"Error calling Ollama: {e}")
        return initial_score
    except Exception as e:
        print(f"Exception running LLM: {e}")
        return initial_score


def main():
    print("Starting main script...")
    try:
        migrated_coins = fetch_migrated_coins_from_pumpfun()
        if not migrated_coins:
            print("No migrated coins found or failed to fetch data.")
        filtered_coins = filter_coins_on_dexscreener(migrated_coins)

        smart_degen_wallets = fetch_smart_degen_wallets()

        results = []
        for coin in filtered_coins:
            addr = coin["address"]
            symbol = coin.get("symbol", "")

            migrated_time_str = coin.get("migrated_time")
            if migrated_time_str:
                try:
                    migrated_time = datetime.fromisoformat(
                        migrated_time_str.replace("Z", "")
                    )
                except:
                    migrated_time = datetime.utcnow()
            else:
                migrated_time = datetime.utcnow()

            age_hours = (datetime.utcnow() - migrated_time).total_seconds() / 3600.0
            if age_hours > 24:
                continue

            holder_data = analyze_holders_gmgn(addr)
            bubble_data = analyze_clusters_bubblemaps(addr)  # Currently not used
            holders = holder_data.get("holders", [])

            max_holder_pct = 0
            if holders:
                max_holder_pct = max(
                    (h.get("supply_pct", 0) for h in holders), default=0
                )

            twitter_score = check_twitter_activity_tweetscout(symbol)
            validity_score = check_validity_solsniffer(addr)

            degen_involvement = check_smart_degen_involvement(
                addr, holders, smart_degen_wallets
            )

            initial_score = calculate_success_rate(
                age_hours, holder_data, twitter_score, validity_score, degen_involvement
            )

            coin_info = {
                "symbol": symbol,
                "address": addr,
                "age_hours": age_hours,
                "max_holder_pct": max_holder_pct,
                "twitter_score": twitter_score,
                "validity_score": validity_score,
                "degen_involvement": degen_involvement,
            }

            llm_score = llm_refine_score_ollama(
                coin_info, initial_score, model="llama2"
            )

            if llm_score > 80:
                recommendation = "Strong Buy"
                hold_time = "1-2 weeks"
            elif llm_score > 60:
                recommendation = "Moderate Buy"
                hold_time = "A few days"
            else:
                recommendation = "Hold off"
                hold_time = "Do not invest"

            results.append(
                {
                    "symbol": symbol,
                    "address": addr,
                    "age_hours": age_hours,
                    "preliminary_score": initial_score,
                    "llm_adjusted_score": llm_score,
                    "recommendation": recommendation,
                    "hold_time": hold_time,
                    "degen_involvement": degen_involvement,
                }
            )

        if not results:
            print("No results after filtering and analysis.")
        else:
            for r in results:
                print("Coin:", r["symbol"])
                print("Address:", r["address"])
                print(f"Age: {r['age_hours']:.2f} hours")
                print("Preliminary Score:", r["preliminary_score"], "/100")
                print("LLM-Adjusted Score:", r["llm_adjusted_score"], "/100")
                print("Smart Degen Involvement:", r["degen_involvement"])
                print("Recommendation:", r["recommendation"])
                print("Suggested Hold Time:", r["hold_time"])
                print("---------------------")
    except Exception as e:
        print(f"Unexpected error in main: {e}")


if __name__ == "__main__":
    main()
