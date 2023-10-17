from fastapi import APIRouter
from fastapi_cache.decorator import cache

from crud.data_crud import country
from schemas.data_schema import ICountryRead
from schemas.response_schema import IResponse, IResponseList, create_response

router = APIRouter()


@router.get("/countries", response_model=IResponseList[ICountryRead])
@cache()
async def get_all_countries():
    countries = await country.get_all()
    return create_response(data=countries)


@router.get("/countries/{code}", response_model=IResponse[ICountryRead])
@cache()
async def get_country_by_code(
    code: str,
):
    country_item = await country.get_by_code(code)
    return create_response(data=country_item)
