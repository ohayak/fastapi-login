from models.battery_model import BatteryCell, BatteryEvolution, BatteryInfo, BatteryModel, BatteryReview, BatteryState


class IBatteryCellRead(BatteryCell):
    pass


class IBatteryModelRead(BatteryModel):
    pass


class IBatteryInfoRead(BatteryInfo):
    pass


class IBatteryEvolutionRead(BatteryEvolution):
    pass


class IBatteryReviewRead(BatteryReview):
    pass


class IBatteryStateRead(BatteryState):
    pass
