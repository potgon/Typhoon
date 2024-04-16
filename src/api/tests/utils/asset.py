import pytest

from database.models import Asset


@pytest.fixture
async def create_test_asset():
    test_asset = await Asset.create(
        ticker="TEST", name="Test asset", asset_type="Stock", sector="Technology"
    )
    yield test_asset
    await test_asset.delete()
