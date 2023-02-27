from uuid import UUID

from fastapi import APIRouter, Depends, status

import crud
from api import deps
from exceptions import ContentNoChangeException, IdNotFoundException, NameExistException
from models.company_model import Company
from models.user_model import User
from schemas.common_schema import PageQuery
from schemas.company_schema import ICompanyCreate, ICompanyRead, ICompanyReadWithUsers, ICompanyUpdate
from schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from schemas.role_schema import IRoleEnum

router = APIRouter()


@router.get("", response_model=IGetResponsePaginated[ICompanyRead])
async def get_companies(
    params: PageQuery = Depends(),
    current_user: User = Depends(deps.get_current_user()),
):
    """
    Gets a paginated list of companies
    """
    companies = await crud.company.get_multi_paginated(params=params)
    return create_response(data=companies)


@router.get("/{company_id}", response_model=IGetResponseBase[ICompanyReadWithUsers])
async def get_company_by_id(
    company_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
):
    """
    Gets a company by its id
    """
    company = await crud.company.get(id=company_id)
    if company:
        return create_response(data=company)
    else:
        raise IdNotFoundException(Company, company_id)


@router.post(
    "",
    response_model=IPostResponseBase[ICompanyRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    company: ICompanyCreate,
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])),
):
    """
    Creates a new company
    """
    company_current = await crud.company.get_company_by_name(name=company.name)
    if company_current:
        raise NameExistException(Company, name=company.name)
    new_company = await crud.company.create(obj_in=company, created_by_id=current_user.id)
    return create_response(data=new_company)


@router.put("/{company_id}", response_model=IPutResponseBase[ICompanyRead])
async def update_company(
    company_id: UUID,
    company: ICompanyUpdate,
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])),
):
    """
    Updates a company by its id
    """
    company_current = await crud.company.get(id=company_id)
    if not company_current:
        raise IdNotFoundException(Company, company_id=company_id)

    if company_current.name == company.name and company_current.description == company.description:
        raise ContentNoChangeException()

    company_updated = await crud.company.update(obj_current=company_current, obj_new=company)
    return create_response(data=company_updated)


@router.post("/add_user/{user_id}/{company_id}", response_model=IPostResponseBase[ICompanyRead])
async def add_user_into_a_company(
    user_id: UUID,
    company_id: UUID,
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])),
):
    """
    Adds a user into a company
    """
    user = await crud.user.get(id=user_id)
    if not user:
        raise IdNotFoundException(User, id=user_id)

    company = await crud.company.get(id=company_id)
    if not company:
        raise IdNotFoundException(Company, company_id)

    company = await crud.company.add_user_to_company(user=user, company_id=company_id)
    return create_response(message="User added to company", data=company)


@router.post("/remove_user/{user_id}/{company_id}", response_model=IPostResponseBase[ICompanyRead])
async def remove_user_from_company(
    user_id: UUID,
    company_id: UUID,
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])),
):
    """
    remove  user from  company list
    """
    user = await crud.user.get(id=user_id)
    if not user:
        raise IdNotFoundException(User, id=user_id)
    company = await crud.company.get(id=company_id)
    if not company:
        raise IdNotFoundException(Company, company_id)
    company = await crud.company.remove_user(user=user, company_id=company_id)
    return create_response(message="User removed from company", data=company)


@router.delete("/{company_id}", response_model=IDeleteResponseBase[ICompanyRead])
async def remove_compamy(
    company_id: UUID,
    current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin])),
):
    """
    Deletes a role by id
    """
    company = await crud.company.get(id=company_id)
    if not company:
        raise IdNotFoundException(Company, company_id)

    company = await crud.company.remove(id=company_id)
    return create_response(data=company)
