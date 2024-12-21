from fastapi import APIRouter

router = APIRouter(tags=["Root"])


@router.get("/health-check", summary="Make a health check")
def health_check():
    return {"status": "ok"}
