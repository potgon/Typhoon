from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `queue` ADD `failed_fetch_date` DATETIME(6) NOT NULL;
        ALTER TABLE `queue` ADD `failed_fetch` BOOL NOT NULL  DEFAULT 0;
        CREATE TABLE IF NOT EXISTS `tempmodel` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `model_name` VARCHAR(50) NOT NULL,
    `training_timestamp` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `performance_metrics` JSON NOT NULL,
    `hyperparameters` JSON NOT NULL,
    `model_architecture` LONGTEXT NOT NULL,
    `serialized_model` LONGBLOB NOT NULL,
    `training_performance` JSON NOT NULL,
    `status` VARCHAR(25) NOT NULL  DEFAULT 'Temporal',
    `asset_id` INT,
    `model_type_id` INT,
    `user_id` INT,
    CONSTRAINT `fk_tempmode_asset_2cf3ebc1` FOREIGN KEY (`asset_id`) REFERENCES `asset` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_tempmode_modeltyp_8e99d81e` FOREIGN KEY (`model_type_id`) REFERENCES `modeltype` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_tempmode_user_069f6851` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        ALTER TABLE `trainedmodel` ADD `training_performance` JSON NOT NULL;
        ALTER TABLE `trainedmodel` DROP COLUMN `training_logs`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `queue` DROP COLUMN `failed_fetch_date`;
        ALTER TABLE `queue` DROP COLUMN `failed_fetch`;
        ALTER TABLE `trainedmodel` ADD `training_logs` LONGTEXT NOT NULL;
        ALTER TABLE `trainedmodel` DROP COLUMN `training_performance`;
        DROP TABLE IF EXISTS `tempmodel`;"""
