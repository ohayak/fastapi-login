from models.battery_model import BatteryCell, BatteryInfo, BatteryModel
from utils.make_model import Model, make_schema_from_orm

# class IBatteryCellRead(BatteryCell):
#     pass


IBatteryCellRead: Model = make_schema_from_orm(BatteryCell, model_name="IBatteryCellRead")


# class IBatteryModelRead(BatteryModel):
#     pass

IBatteryModelRead: Model = make_schema_from_orm(BatteryModel, model_name="IBatteryModelRead")


# class IBatteryInfoRead(BatteryInfo):
#     pass

IBatteryInfoRead: Model = make_schema_from_orm(BatteryInfo, model_name="IBatteryInfoRead")


# class IBatteryEvolutionRead(BatteryEvolution):
#     pass


# class IBatteryReviewRead(BatteryReview):
#     pass


# class IBatteryStateRead(BatteryState):
#     pass
