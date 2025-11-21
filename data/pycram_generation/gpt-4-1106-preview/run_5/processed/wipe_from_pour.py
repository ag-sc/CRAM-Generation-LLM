class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_cloth, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the cloth: {self.object_cloth} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            start_x = self.wipe_location.position[0] - self.length / 2
            start_y = self.wipe_location.position[1] - self.width / 2
            end_x = start_x + self.length
            end_y = start_y + self.width
            gap = 0.1  
            strip_y = start_y
            while strip_y <= end_y:
                strip_start_pose = Pose([start_x, strip_y, self.wipe_location.position[2]], self.wipe_location.orientation)
                MoveTCPMotion(strip_start_pose, self.arm).resolve().perform()
                strip_end_pose = Pose([end_x, strip_y, self.wipe_location.position[2]], self.wipe_location.orientation)
                MoveTCPMotion(strip_end_pose, self.arm).resolve().perform()
                strip_y += gap
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(cloth_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
