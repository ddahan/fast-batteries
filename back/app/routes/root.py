from fastapi import APIRouter

router = APIRouter(tags=["Root"])


# HEAD method is required to work with wget util
@router.api_route("/health-check", methods=["GET", "HEAD"], summary="Make a health check")
def health_check():
    return {"status": "ok"}
