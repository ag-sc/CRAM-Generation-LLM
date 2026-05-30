class TransportAction(ActionDesignatorDescription):
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], target_locations: List[Pose], resolver=None):
        super().__init__(resolver)
        self.object_designator_description = object_designator_description
        self.arms = arms
        self.target_locations = target_locations
    def ground(self) -> Action:
        object_desig = self.object_designator_description if (isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) or isinstance(self.object_designator_description, ObjectPart.Object)) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.target_locations)
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        target_locations: List[Pose]
        @with_tree
        def perform(self) -> None:
            PickUpAction(self.object_desig, [self.arm], [], resolver=None).resolve().perform()
            NavigateAction(self.target_locations, resolver=None).resolve().perform()
            PlaceAction(self.object_desig, self.target_locations, [self.arm], resolver=None).resolve().perform()
