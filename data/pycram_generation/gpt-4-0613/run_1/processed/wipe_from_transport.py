class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        arm: str
        wipe_location: Pose
        length: float
        width: float
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_cloth, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_cloth} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            wipe_loc = CostmapLocation(target=self.wipe_location, reachable_for=robot_desig.resolve(), reachable_arm=self.arm).resolve()
            NavigateAction([wipe_loc.pose]).resolve().perform()
            num_strips = math.ceil(self.length / 0.1)
            for i in range(num_strips):
                start_x = self.wipe_location.position[0] - self.length / 2 + i * 0.1
                start_y = self.wipe_location.position[1] - self.width / 2
                end_x = start_x
                end_y = self.wipe_location.position[1] + self.width / 2
                start_pose = Pose([start_x, start_y, self.wipe_location.position[2]], self.wipe_location.orientation)
                end_pose = Pose([end_x, end_y, self.wipe_location.position[2]], self.wipe_location.orientation)
                MoveTCPMotion.Action(start_pose, self.arm).perform()
                MoveTCPMotion.Action(end_pose, self.arm).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        obj_cloth = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(obj_cloth, self.arms[0], self.wipe_locations[0], self.lengths[0], self.widths[0])
