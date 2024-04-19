from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `modeltype` MODIFY COLUMN `description` JSON NOT NULL;
        ALTER TABLE `tempmodel` MODIFY COLUMN `model_architecture` JSON NOT NULL;
        ALTER TABLE `trainedmodel` MODIFY COLUMN `model_architecture` JSON NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `modeltype` MODIFY COLUMN `description` LONGTEXT NOT NULL;
        ALTER TABLE `tempmodel` MODIFY COLUMN `model_architecture` LONGTEXT NOT NULL;
        ALTER TABLE `trainedmodel` MODIFY COLUMN `model_architecture` LONGTEXT NOT NULL;"""
