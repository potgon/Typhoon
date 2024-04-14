from fastapi import APIRouter, HTTPException
from typing import List, Union, Dict
import yfinances as yf

from database.models import Asset
from api.schemas import AssetModel
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

    msg_body = {}

    info_dict = {}
    for asset in tickers:
        try:
            data = yf.Ticker(asset).info
            info_dict[asset] = {
                "ticker": asset,
                "name": data.get("shortName", None),
                "asset_type": data.get("quoteType", None),
                "sector": data.get("sector", None),
            }
            await Asset(
                ticker=asset,
                name=data.get("shortName", None),
                asset_type=data.get("quoteType", None),
                sector=data.get("sector", None),
            ).save()
            msg_body[asset] = "Data stored"
        except Exception as e:
            make_log(
                "ASSETS",
                40,
                "api_error.log",
                f"Error fetching data for {asset}: {str(e)}",
            )
            msg_body[asset] = "Error fetching data"
            continue
    return {"message": msg_body}
