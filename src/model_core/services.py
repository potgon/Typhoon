from .trainer import Trainer
from utils.logger import make_log
from database.models import Queue

from datetime import datetime, timezone
from tortoise.exceptions import IncompleteInstanceError, IntegrityError


async def service_loop() -> None:
    trainer = Trainer()
    while True:
        try:
            trainer.train()
        except TypeError as e:
            make_log(
                "TRAINER_SERVICE",
                40,
                "trainer_error.log",
                f"Failed at request: {trainer.current_request.id}. Trainer train method error: {str(e)}. Skipping request.",
            )
            manage_failed_request(trainer.current_request)
            continue
        trainer.evaluate()
        model = trainer.save_model()
        if model is None:
            make_log(
                "TRAINER_SERVICE",
                30,
                "trainer_error.log",
                "Error saving model, continuing with service...",
            )


async def manage_failed_request(request: Queue) -> None:
    request.failed_fetch = True
    request.failed_fetch_date = datetime.now(timezone.utc)
    try:
        await request.save(update_fields=["failed_fetch, failed_fetch_date"])
    except (IncompleteInstanceError, IntegrityError) as e:
        make_log(
            "TRAINER_SERVICE",
            40,
            "trainer_error.log",
            f"Failed request could not be updated: {str(e)}",
        )
