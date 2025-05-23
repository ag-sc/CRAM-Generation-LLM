
class TransportAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        target_location: Pose

        @with_tree
        def perform(self) -> None:
            pick_up_action = PickUpAction(self.object_designator, [self.arm], resolver=self.resolver)
            pick_up_action.resolve().perform()

            navigate_action = NavigateAction([self.target_location], resolver=self.resolver)
            navigate_action.resolve().perform()

            place_action = PlaceAction(self.object_designator, [self.target_location], [self.arm], resolver=self.resolver)
            place_action.resolve().perform()

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], target_locations: List[Pose], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.target_locations: List[Pose] = target_locations

    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.target_locations[0])
