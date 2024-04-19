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
            PickUpAction.Action(self.object_cloth, self.arms, "top").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            cloth_dimensions = self.object_cloth.bullet_world_object.get_object_dimensions()
            for i, wipe_loc in enumerate(self.wipe_locations):
                wipe_loc = CostmapLocation(target=wipe_loc, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
                try:
                    wipe_pose = next(iter(wipe_loc))
                except StopIteration:
                    raise ReachabilityFailure(f"Found no pose for the robot to wipe at location {i}")
                NavigateAction([wipe_pose.pose]).resolve().perform()
                gripper_pose = Pose([wipe_pose.pose.position.x, wipe_pose.pose.position.y, wipe_pose.pose.position.z+0.1], [1, 0, 0, 1])
                MoveTCPMotion(gripper_pose, self.arms[0]).resolve().perform()
                length = self.lengths[i]
                width = self.widths[i]
                num_strips = math.ceil(width / 0.1)
                for j in range(num_strips):
                    if j % 2 == 0:
                        start_x = -length/2
                        end_x = length/2
                    else:
                        start_x = length/2
                        end_x = -length/2
                    start_y = -width/2 + j*0.1
                    end_y = start_y
                    start_pose = Pose([start_x, start_y, gripper_pose.pose.position.z], [1, 0, 0, 1])
                    end_pose = Pose([end_x, end_y, gripper_pose.pose.position.z], [1, 0, 0, 1])
                    MoveTCPMotion(start_pose, self.arms[0]).resolve().perform()
                    MoveTCPMotion(end_pose, self.arms[0]).resolve().perform()
                ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
