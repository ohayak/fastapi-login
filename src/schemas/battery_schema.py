from pydantic import BaseModel, create_model
from sqlmodel import SQLModel

from models.battery_model import (
    BatteryCell,
    BatteryCompany,
    BatteryEvolution,
    BatteryInfo,
    BatteryModel,
    BatteryReview,
    BatteryState,
    CompanyData,
)
from utils.make_model import Model, make_schema_from_orm, merge_schemas

IBatteryCellRead: Model = make_schema_from_orm(BatteryCell, model_name="IBatteryCellRead")


IBatteryModelRead: Model = make_schema_from_orm(BatteryModel, model_name="IBatteryModelRead")


IBatteryInfoRead: Model = make_schema_from_orm(BatteryInfo, model_name="IBatteryInfoRead")


IBatteryEvolutionRead: Model = make_schema_from_orm(BatteryEvolution, model_name="IBatteryEvolutionRead")


IBatteryReviewRead: Model = make_schema_from_orm(BatteryReview, model_name="IBatteryReviewRead")


IBatteryStateRead: Model = make_schema_from_orm(BatteryState, model_name="IBatteryStateRead")


IBatteryCompanyRead: Model = make_schema_from_orm(BatteryCompany, model_name="IBatteryCompanyRead")


ICompanyDataRead: Model = make_schema_from_orm(CompanyData, model_name="ICompanyDataRead")


IBatteryCompanyDataRead: Model = merge_schemas(
    (
        IBatteryCompanyRead,
        ICompanyDataRead,
    ),
    schema_name="IBatteryCompanyDataRead",
    exclude=("company_id",),
)
