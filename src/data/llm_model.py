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
    ticker: Optional[str] = Field(
        None, description="The ticker of the token", alias="ticker"
    )
    name: Optional[str] = Field(None, description="The name of the token", alias="name")


class token_address(BaseModel):
    full_address: str = Field(None, description="The address of the token")

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
    dev_sold_bought: Optional[str] = Field(
        None, description="Developer sold/bought status", alias="dev sold/bought"
    )
    age: Optional[str] = Field(None, description="Age of the token", alias="age")
    address: Optional[str] = Field(
        None, description="Address of the token", alias="address"
    )
    liquidity: Optional[str] = Field(
        None, description="Liquidity of the token", alias="liquidity"
    )
    total_holders: Optional[str] = Field(
        None, description="Total number of holders", alias="total holders"
    )
    volume: Optional[str] = Field(
        None, description="Volume of the token", alias="volume"
    )
    market_cap: Optional[str] = Field(
        None, description="Market cap of the token", alias="market cap"
    )

    @field_validator("*", mode="before")
    def validate_fields(cls, v, field):
        if v is None or v == "":
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


class valid_data(BaseModel):
    pumpfun_data: gmgn_main_data | PumpfunData
    gmgn_data: gmgn_data
    holders: holders_data

    @field_validator("*")
    def check_data(cls, v):
        if not v:
            raise ValueError("Data is empty")
        if isinstance(v, dict) and not v:
            raise ValueError("Dictionary cannot be empty")
        return v
