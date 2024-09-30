class TransportAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_desig: ObjectDesignatorDescription.Object
        arm: str
        target_location: Pose
        def perform(self) -> None:
            PickUpAction(self.object_desig, [self.arm]).resolve().perform()
            PlaceAction(self.object_desig, [self.target_location], [self.arm]).resolve().perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], target_locations: List[Pose], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms
        self.target_locations = target_locations
    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0], self.target_locations[0])
