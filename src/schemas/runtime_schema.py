from models.runtime_model import BatteryEvolution, BatteryInfo
from utils.make_model import Model, make_schema_from_orm

IBatteryInfoRead: Model = make_schema_from_orm(BatteryInfo, model_name="IBatteryInfoRead")


IBatteryEvolutionRead: Model = make_schema_from_orm(BatteryEvolution, model_name="IBatteryEvolutionRead")


IBatteryStateInfoRead: Model = make_schema_from_orm(
    BatteryInfo,
    BatteryEvolution,
    model_name="IBatteryStateInfoRead",
)
