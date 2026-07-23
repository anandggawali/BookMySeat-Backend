from fastapi import APIRouter
from services.config_service import ConfigurationService

router = APIRouter(
    prefix="/api",
    tags=["Configuration"]
)


@router.get("/config")
def get_configuration():
    return ConfigurationService.get_configuration()