from fastapi import APIRouter, HTTPException
from typing import List

from database.models import Queue
from api.schemas import QueueModel

router = APIRouter()

@router.get("/queue/")
def queue_position():
    pass

