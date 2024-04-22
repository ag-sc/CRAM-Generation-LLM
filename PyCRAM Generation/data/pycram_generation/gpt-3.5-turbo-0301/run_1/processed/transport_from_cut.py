class TransportAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        target_locations: List[Pose]
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)
        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_designator.data_copy()
            object = self.object_designator.bullet_world_object
            for target_location in self.target_locations:
                object_location = CostmapLocation(object, reachable_for=object, visible_for=object, reachable_arm=self.arm).resolve()
                NavigateAction([object_location]).resolve().perform()
                PickUpAction(self.object_designator, [self.arm], robot_description.grasps.get_grasps_for_object(self.object_designator), resolver=None).resolve().perform()
                target_location = CostmapLocation(target_location, reachable_for=object, visible_for=object, reachable_arm=self.arm).resolve()
                NavigateAction([target_location]).resolve().perform()
                PlaceAction(self.object_designator, [target_location], [self.arm], resolver=None).resolve().perform()
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], target_locations: List[Pose], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.target_locations: List[Pose] = target_locations
    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.target_locations)
