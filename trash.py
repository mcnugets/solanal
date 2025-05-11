headers_pumpfun = [
    "coin name",
    "fullname",
    "bd",
    "mc",
    "vol",
    "t10",
    "holders",
    "age",
    "dh",
    "snipers",
    "address",
]
headers_gmgn_1 = [
    "ticker",
    "name",
    "dev sold/bought",
    "age",
    "address",
    "liquidity",
    "total holders",
    "volume",
    "market cap",
    "full_address",
]


# TRUMP    = name
# THE ALMI
# 0%
# Run     = dev sold
# Fkr7i...8tU = address
# $0.0₅83176 = current price
# 0%       = 24h
# 0/1      = snipers
# 0%       = bluechip
# 0%      = top 10
# Safe    = audit
# 4/4
headers_gmgn = [
    "ticker",
    "name",
    "i dont know",
    "dev sold?",
    "address",
    "current price",
    "24h",
    "snipers",
    "bluechip",
    "top 10",
    "audit",
    "Taxes",
    "full_address",
]

#  URL = "https://solscan.io/token/"
#     main_locator = (
#         By.XPATH,
#         "/html/body/div/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div/div[5]/div/div/div[1]/div/button",
#     )
#     row_locator = (By.XPATH, "/html/body/div[3]/div[3]/button[2]")
#     ss = solscan_processor(
#         main_locator=main_locator,
#         popup_locator=(),
#         row_locator=row_locator,
#         url=URL,
#         csv_path="../pumpfun_data.csv",
#         download_path="../holders",
#         driver_path=r"C:\Users\sulta\AppData\Local\Programs\Python\Python310\lib\site-packages\chromedriver_autoinstaller\131\chromedriver.exe",
#     )


# pumpfun_config = {
#     "type": "pumpfun",
#     "url": "https://pump.fun/advanced",
#     "row_locator": (By.TAG_NAME, "tr"),
#     "popup_locator": (By.XPATH, "/html/body/div[4]/div[5]/button"),
#     "main_locator": (  # change main locator to pumfun
#         By.XPATH,
#         "/html/body/div[1]/div/div/main/div[2]/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div",
#     ),
#     "driver_path": driver_path,
#     "div_locator": (
#         By.XPATH,
#         " /html/body/div[1]/main/div[1]/main/div/div[3]/div[2]/div/div/table/tbody/tr[1]/td[1]",
#     ),
# }
# gmgn_config_2 = {
#     "type": "pumpfun",
#     "url": "https://gmgn.ai/new-pair/tCkVIIwp?chain=sol",
#     "row_locator": (By.CLASS_NAME, "g-table-row"),
#     "popup_locator": (By.XPATH, "/html/body/div[3]/div/div[3]"),
#     "main_locator": (
#         By.XPATH,
#         "/html/body/div[1]/div/div/main/div[2]/div[2]/div[1]/div/div[1]/div[3]/div/div/div/div/div/div[1]/div/div",
#     ),
#     "driver_path": driver_path,
# }

# gmgn_config = {
#     "type": "gmgn",
#     "url": "https://gmgn.ai/sol/token/",
#     "row_locator": (By.CLASS_NAME, "css-1jy8g2v"),
#     "popup_locator": (By.XPATH, "/html/body/div[3]/div/div[3]"),
#     "driver_path": driver_path,
#     "main_locator": (By.CLASS_NAME, "css-1jy8g2v"),
#     "csv_path": "pumpfun_data.csv",
# }
