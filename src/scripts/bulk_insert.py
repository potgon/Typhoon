import yfinance as yf

from database.models import Asset


async def bulk_insert_data():
    asset_list = []  # fill with yfinance tickers
    info_dict = {}
    for asset in asset_list:
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
        except Exception as e:
            print(f"Error fetching data for {asset}: {str(e)}")
            continue
