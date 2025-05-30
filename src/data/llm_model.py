from pydantic import BaseModel, field_validator, Field
from typing import List, Optional, Dict


# headers = [
#     "ticker",
#     "name",
#     "bd",
#     "mc",
#     "vol",
#     "t10",
#     "holders",
#     "age",
#     "dh",
#     "snipers",
#     "full_address",
# ]
# headers_gmgn_1 = [
#     "ticker",
#     "name",
#     "dev sold/bought",
#     "age",
#     "address",
#     "liquidity",
#     "total holders",
#     "volume",
#     "market cap",
#     "full_address",
# ]
# headers_gmgn = [
#     "ticker",
#     "name",
#     "i dont know",
#     "dev sold?",
#     "address",
#     "current price",
#     "24h",
#     "snipers",
#     "bluechip",
#     "top 10",
#     "audit",
#     "Taxes",
#     "full_address",
# ]


class token_basic(BaseModel):
    ticker: Optional[str] = Field(description="The ticker of the token", alias="ticker")
    name: Optional[str] = Field(description="The name of the token", alias="name")


class token_address(BaseModel):
    full_address: str = Field(description="The address of the token")

    @field_validator("*")
    def address_validator(cls, v):
        if not v:
            raise ValueError("Address is empty")
        return v


class PumpfunData(token_address, token_basic):

    bd: Optional[str] = Field(None, description="Buy/Sell difference indicator")
    mc: Optional[str] = Field(None, description="Market capitalization in USD")
    vol: Optional[str] = Field(None, description="24h trading volume in USD")
    t10: Optional[str] = Field(None, description="Percentage held by top 10 holders")
    holders: Optional[str] = Field(
        None, description="Total number of unique token holders"
    )
    age: Optional[str] = Field(None, description="Time elapsed since token creation")
    dh: Optional[str] = Field(None, description="24h price change percentage")
    snipers: Optional[str] = Field(
        None, description="Number of detected sniper wallets"
    )

    @field_validator("*", mode="before")
    def validate_fields(cls, v, field):
        """Validate all fields are not empty when provided."""
        if v is not None and not str(v).strip():
            raise ValueError(f"{field.name} cannot be empty if provided")
        return v


class gmgn_main_data(token_address, token_basic):
    age: str = Field(
        description="Age of the token", alias="age"
    )
    address: str = Field(
        description="Address of the token", alias="address"
    )
    liquidity: Optional[str] = Field(None,
        description="Liquidity of the token", alias="liquidity"
    )
    total_holders: str = Field(
        description="Total number of holders", alias="total holders"
    )
    volume: str = Field(
        description="Volume of the token", alias="volume"
    )
    market_cap: str = Field(
        description="Market cap of the token", alias="market cap"
    )
    top_10: Optional[str] = Field(
        None, description="Percentage held by top 10 holders", alias="Top 10"
    )
    dev_holds: Optional[str] = Field(
        None, description="Percentage of tokens held by dev", alias="Dev holds"
    )
    insiders: Optional[str] = Field(
        None, description="Insider activity status", alias="insiders"
    )
    snipers: Optional[str] = Field(
        None, description="Number of sniper wallets detected", alias="snipers"
    )
    rug: Optional[str] = Field(
        None, description="Rug pull risk indicator", alias="rug"
    )
    migrated: Optional[str] = Field(
        None, description="How many dev coins migrated", alias="migrated"
    )

    @field_validator("*", mode="before")
    def validate_fields(cls, v, field):
        if v is None:
            raise ValueError(f"{field.name} cannot be empty")
        return v

    class Config:
        populate_by_name = True  # Allows both original and alias names


# "ticker","name","dev sold/bought","age","address","liquidity","total holders","volume","market cap","full_address"


class gmgn_data(token_address, token_basic):
    i_dont_know: Optional[str] = Field(
        None, description="Unspecified metric", alias="i dont know"
    )
    dev_sold: Optional[str] = Field(
        None, description="Developer sell status", alias="dev sold?"
    )
    address: Optional[str] = Field(None, description="Token address", alias="address")
    current_price: Optional[str] = Field(
        None, description="Current token price in USD", alias="current price"
    )
    time_24_h: Optional[str] = Field(
        None, description="24-hour price change", alias="24h"
    )
    snipers: Optional[str] = Field(
        None, description="Number of sniper wallets", alias="snipers"
    )
    bluechip: Optional[str] = Field(
        None, description="Blue chip status indicator", alias="bluechip"
    )
    top_10: Optional[str] = Field(
        None, description="Top 10 holders percentage", alias="top 10"
    )
    audit: Optional[str] = Field(
        None, description="Audit status of the contract", alias="audit"
    )
    taxes: Optional[str] = Field(
        None, description="Token transaction tax rates", alias="Taxes"
    )

    class Config:
        populate_by_name = True


# "ticker","name","i dont know","dev sold?","address","current price","24h","snipers","bluechip","top 10","audit","Taxes","full_address"


class holders_data(BaseModel):
    Account: Dict[int, str] = Field(description="Account addresses by index")
    Token_Account: Dict[int, str] = Field(
        alias="Token Account", description="Token addresses by index"
    )
    Quantity: Dict[int, float] = Field(description="Token quantities by index")
    Percentage: Dict[int, float] = Field(description="Holding percentages by index")

    class Config:
        populate_by_name = True  # Allows both original and alias names

# TODO: GOTTA WORK ON THIS VALIDATION NOT SURE HOW TO PROPERLY STRUCTURE IT
class valid_data(BaseModel):
    gmgn_2: gmgn_main_data | PumpfunData | None =  Field(None, alias="gmgn_2")
    gmgn_data_: gmgn_data | None = None
    holders: holders_data | None = None

    @field_validator("*")
    def check_data(cls, v):
        if not v:
            raise ValueError("Data is empty")
        if isinstance(v, dict) and not v:
            raise ValueError("Dictionary cannot be empty")
        return v
