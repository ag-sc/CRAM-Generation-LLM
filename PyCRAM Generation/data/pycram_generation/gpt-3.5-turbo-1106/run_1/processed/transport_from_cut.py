class TransportAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        target_locations: List[Pose]
        @with_tree
        def perform(self) -> None:
            object = self.object_designator.resolve()
            target_location = self.target_locations[0]
            PickUpAction(object, [self.arm], ["default"]).resolve().perform()
            NavigateAction([target_location]).resolve().perform()
            PlaceAction(object, [target_location], [self.arm]).resolve().perform()
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], target_locations: List[Pose], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.target_locations: List[Pose] = target_locations
    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.target_locations)
