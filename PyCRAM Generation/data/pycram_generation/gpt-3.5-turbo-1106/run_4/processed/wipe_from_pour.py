class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_cloth, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_cloth} with arm: {self.arms[0]}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth, self.arms[0], "top").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            wipe_poses = []
            for loc, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                center = loc.position
                x_axis = [1, 0, 0]
                y_axis = [0, 1, 0]
                z_axis = [0, 0, 1]
                half_length = length / 2
                half_width = width / 2
                start = [center[0] - half_length, center[1] - half_width, center[2]]
                end = [center[0] + half_length, center[1] + half_width, center[2]]
                wipe_poses.append(Pose(start, [1, 0, 0, 1]))
                wipe_poses.append(Pose(end, [1, 0, 0, 1]))
            wipe_loc = CostmapLocation(target=wipe_poses, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                wipe_pose = next(iter(wipe_loc))
            except StopIteration:
                raise ReachabilityFailure(f"Found no pose for the robot to wipe with arm: {self.arms[0]}")
            NavigateAction([wipe_pose.pose]).resolve().perform()
            for i in range(len(wipe_poses) - 1):
                MoveTCPMotion(wipe_poses[i], self.arms[0]).resolve().perform()
                MoveTCPMotion(wipe_poses[i+1], self.arms[0]).resolve().perform()
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
        return self.Action(cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
