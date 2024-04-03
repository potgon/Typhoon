from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `asset` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `ticker` VARCHAR(20) NOT NULL UNIQUE,
    `name` VARCHAR(50) NOT NULL,
    `asset_type` VARCHAR(50) NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `modeltype` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `model_name` VARCHAR(50) NOT NULL UNIQUE,
    `description` LONGTEXT NOT NULL,
    `default_hyperparameters` JSON NOT NULL,
    `default_model_architecture` LONGTEXT NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `username` VARCHAR(30) NOT NULL UNIQUE,
    `password` VARCHAR(128) NOT NULL,
    `email` VARCHAR(50) NOT NULL UNIQUE,
    `first_name` VARCHAR(50),
    `last_name` VARCHAR(50),
    `date_joined` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `is_active` BOOL NOT NULL  DEFAULT 1,
    `is_staff` BOOL NOT NULL  DEFAULT 0,
    `priority` BOOL NOT NULL  DEFAULT 0,
    `tokens` INT NOT NULL  DEFAULT 0
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `queue` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `priority` BOOL NOT NULL  DEFAULT 0,
    `asset_id` INT NOT NULL,
    `model_type_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_queue_asset_54e96281` FOREIGN KEY (`asset_id`) REFERENCES `asset` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_queue_modeltyp_fc151fab` FOREIGN KEY (`model_type_id`) REFERENCES `modeltype` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_queue_user_247d0c60` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `trainedmodel` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `model_name` VARCHAR(50) NOT NULL,
    `training_timestamp` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `performance_metrics` JSON NOT NULL,
    `hyperparameters` JSON NOT NULL,
    `model_architecture` LONGTEXT NOT NULL,
    `serialized_model` LONGBLOB NOT NULL,
    `training_logs` LONGTEXT NOT NULL,
    `status` VARCHAR(25) NOT NULL  DEFAULT 'Inactive',
    `asset_id` INT,
    `model_type_id` INT,
    `user_id` INT,
    CONSTRAINT `fk_trainedm_asset_3f862fec` FOREIGN KEY (`asset_id`) REFERENCES `asset` (`id`) ON DELETE NO ACTION,
    CONSTRAINT `fk_trainedm_modeltyp_320fe302` FOREIGN KEY (`model_type_id`) REFERENCES `modeltype` (`id`) ON DELETE NO ACTION,
    CONSTRAINT `fk_trainedm_user_e10377fc` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
