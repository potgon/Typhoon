from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `asset` ADD `sector` VARCHAR(50);
        ALTER TABLE `asset` MODIFY COLUMN `asset_type` VARCHAR(50);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `asset` DROP COLUMN `sector`;
        ALTER TABLE `asset` MODIFY COLUMN `asset_type` VARCHAR(50) NOT NULL;"""
