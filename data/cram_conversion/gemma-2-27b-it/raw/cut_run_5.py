@dataclasses.dataclass
class CutActionDesignator(ActionDesignatorDescription):
    object_designator: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object]
    arm: str
    grasp: str
    cut_type: str = "slice" # "slice" or "halving"

    def __post_init__(self):
        self.object_designator = self.object_designator

    def ground(self, world: BulletWorld, local_transformer: LocalTransformer) -> ActionDesignatorDescription:
        # ...
        # Implement the logic to ground the CutActionDesignator
        # ...
        return grounded_action_designator