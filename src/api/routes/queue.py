from fastapi import APIRouter, HTTPException, Depends
from typing import Dict

from database.models import Queue, User
from api.deps import get_current_user

router = APIRouter()


@router.get("/")
async def user_queue_position(current_user: User = Depends(
        get_current_user)) -> Dict[str, dict[str, int]]:
    first_item = await Queue.first()
    if not first_item:
        raise HTTPException(status_code=404, detail="Queue is empty")

    user_queue_items = await Queue.filter(user=current_user).all()
    if not user_queue_items:
        raise HTTPException(
            status_code=404,
            detail="User has no enqueued models for training")

    user_positions = {}
    for item in user_queue_items:
        rows_before = await Queue.filter(id__lt=item.id).count()
        user_positions[item.model_type] = rows_before

    return {"user_positions": user_positions}
