class TransportAction(ActionDesignatorDescription):
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], target_locations: List[Pose], resolver=None):
        super(TransportAction, self).__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.target_locations: List[Pose] = target_locations

    def __iter__(self):
        for object_, arm, target_location in itertools.product(iter(self.object_designator_description), self.arms, self.target_locations):
            yield self.Action(object_, arm, target_location)

    def ground(self) -> Action:
        return next(iter(self))

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        target_location: Pose

        def perform(self) -> None:
            PickUpAction(self.object_designator, [self.arm], ['left'], resolver=None).resolve().perform()
            NavigateAction([self.target_location], resolver=None).resolve().perform()
            PlaceAction(self.object_designator, [self.target_location], [self.arm], resolver=None).resolve().perform()