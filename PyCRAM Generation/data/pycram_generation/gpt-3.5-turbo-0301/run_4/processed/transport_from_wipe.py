class TransportAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object: ObjectDesignatorDescription.Object
        arms: List[str]
        target_locations: List[Pose]
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object} with arm: {self.arms[0]}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object, self.arms, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            place_loc = CostmapLocation(target=self.target_locations[0], reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                place_pose = next(iter(place_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to place the object: {self.object} at location: {self.target_locations[0]} with arm: {self.arms[0]}")
            NavigateAction([place_pose.pose]).resolve().perform()
            PlaceAction.Action(self.object, self.target_locations, self.arms).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], target_locations: List[Pose], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.target_locations: List[Pose] = target_locations
    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms, self.target_locations[0])
