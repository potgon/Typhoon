from fastapi import APIRouter, HTTPException
from typing import List, Union, Dict
import yfinance as yf
from tortoise.exceptions import IncompleteInstanceError, IntegrityError

from database.models import Asset
from api.schemas import AssetModel, AssetCheck
from utils.logger import make_log

router = APIRouter()


@router.get("/", response_model=List[AssetModel])
async def read_all_assets():
    asset_queryset = await Asset.all()
    if asset_queryset is None:
        raise HTTPException(
            status_code=500, detail="Server error: assets could not be retrieved"
        )
    return asset_queryset


@router.get("/{ticker}", response_model=AssetModel)
async def read_asset(ticker: str):
    asset = await Asset.filter(ticker=ticker).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.post("/bulk-add")
async def bulk_add(tickers: Union[str, List[str]]) -> Dict[str, Dict[str, str]]:
    if isinstance(tickers, str):
        tickers = [tickers]

    response = {}

    info_dict = {}
    for ticker in tickers:
        try:
            data = yf.Ticker(ticker).info
        except Exception as e:
            make_log(
                "ASSETS",
                40,
                "api_error.log",
                f"Error fetching data for {ticker}: {str(e)}",
            )
            response[ticker] = "Error fetching data"
            continue
        if data.get("shortName") is None:
            response[ticker] = "No data found. Ticker might be invalid"
            continue
        info_dict[ticker] = {
            "ticker": ticker,
            "name": data.get("shortName", None),
            "asset_type": data.get("quoteType", None),
            "sector": data.get("sector", None),
        }
        try:
            await Asset(
                ticker=ticker,
                name=data.get("shortName", None),
                asset_type=data.get("quoteType", None),
                sector=data.get("sector", None),
            ).save()
            response[ticker] = "Data stored"
        except (IncompleteInstanceError) as e:
            make_log(
                "ASSETS",
                40,
                "api_error.log",
                f"Error saving asset data to database for {ticker}: {str(e)}",
            )
            response[ticker] = "Error saving to database"
            continue
        except (IntegrityError) as e:
            make_log(
                "ASSETS",
                40,
                "api_error.log",
                f"Asset already present in database? {str(e)}",
            )
            response[ticker] = "Asset already present in database"
            continue
    return {"message": response}
