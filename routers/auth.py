from fastapi import APIRouter

router = APIRouter(
    prefix="/auth",  # API'nin URL yolu, yani endpointlerin başına auth koyulur
    tags=["Authentication"]  #Swaggerda başlık tagsler
)

#@router.get("/")