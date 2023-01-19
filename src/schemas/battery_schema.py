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
from utils.make_model import Model, make_schema_from_orm

IBatteryCellRead: Model = make_schema_from_orm(BatteryCell, model_name="IBatteryCellRead")


IBatteryModelRead: Model = make_schema_from_orm(BatteryModel, model_name="IBatteryModelRead")


IBatteryInfoRead: Model = make_schema_from_orm(BatteryInfo, model_name="IBatteryInfoRead")


IBatteryEvolutionRead: Model = make_schema_from_orm(BatteryEvolution, model_name="IBatteryEvolutionRead")


IBatteryReviewRead: Model = make_schema_from_orm(BatteryReview, model_name="IBatteryReviewRead")


IBatteryStateRead: Model = make_schema_from_orm(BatteryState, model_name="IBatteryStateRead")


IBatteryStateInfoRead: Model = make_schema_from_orm(
    BatteryInfo,
    BatteryState,
    model_name="IBatteryStateInfoRead",
)


IBatteryCompanyDataRead: Model = make_schema_from_orm(
    BatteryCompany, CompanyData, model_name="IBatteryCompanyDataRead", exclude=("company_id",)
)
