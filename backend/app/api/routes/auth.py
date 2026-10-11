# app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_auth_service, get_current_user
from app.schemas.auth import Token
from app.schemas.user import UserInfo
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.login(
        email=form_data.username,
        password=form_data.password,
    )

@router.get("/me", response_model=UserInfo, status_code=status.HTTP_200_OK)
async def get_user_info(
    current_user: dict =  Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.get_user_info(current_user["requester"])
