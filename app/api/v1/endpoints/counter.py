from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any
from ....services.visit_counter import VisitCounterService
from ....schemas.counter import VisitCount


router = APIRouter()

# Dependency to get VisitCounterService instance
def get_visit_counter_service():
    from ....main import visit_counter_service
    return visit_counter_service

@router.post("/visit/{page_id}")
async def record_visit(
    page_id: str,
    counter_service: VisitCounterService = Depends(get_visit_counter_service)
):
    """Record a visit for a website"""
    try:
        await counter_service.increment_visit(page_id)
        return {"status": "success", "message": f"Visit recorded for page {page_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/visits/{page_id}", response_model=VisitCount)
async def get_visits(
    background_task: BackgroundTasks,
    page_id: str,
    counter_service: VisitCounterService = Depends(get_visit_counter_service)
):
    """Get visit count for a website"""
    try:
        count, served_via = await counter_service.get_visit_count(page_id)
        return VisitCount(visits=count, served_via=served_via)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 