from fastapi import APIRouter, Body, Path, status


router = APIRouter()


@router.get("/auth/token")
def post_token():
    pass
