from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "app": "Voice Command Shopping Assistant",
        "version": "0.1.0"
    }
