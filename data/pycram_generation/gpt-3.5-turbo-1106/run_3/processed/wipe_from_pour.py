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
            for i in range(len(self.wipe_locations)):
                wipe_loc = CostmapLocation(target=self.wipe_locations[i], reachable_for=robot_desig.resolve(), reachable_arm=self.arms[i%len(self.arms)])
                try:
                    wipe_pose = next(iter(wipe_loc))
                except StopIteration:
                    raise ReachabilityFailure(f"Found no pose for the robot to wipe at location: {self.wipe_locations[i]} with arm: {self.arms[i%len(self.arms)]}")
                NavigateAction([wipe_pose.pose]).resolve().perform()
                length = self.lengths[i]
                width = self.widths[i]
                cloth_dimensions = self.object_cloth.bullet_world_object.get_object_dimensions()
                cloth_length = cloth_dimensions[0]
                cloth_width = cloth_dimensions[1]
                num_strips = math.ceil(length / 0.1)
                num_passes = math.ceil(width / 0.1)
                for _ in range(num_passes):
                    for _ in range(num_strips):
                        start_pose = Pose([wipe_pose.pose.position.x - 0.5*length, wipe_pose.pose.position.y - 0.5*width, wipe_pose.pose.position.z], wipe_pose.pose.orientation)
                        end_pose = Pose([start_pose.position.x + length, start_pose.position.y, start_pose.position.z], start_pose.orientation)
                        MoveTCPMotion(start_pose, self.arms[i%len(self.arms)]).resolve().perform()
                        MoveTCPMotion(end_pose, self.arms[i%len(self.arms)]).resolve().perform()
                        start_pose, end_pose = end_pose, start_pose
                    wipe_pose.pose.position.y += 0.1
                    wipe_pose.pose.orientation = multiply_quaternions(wipe_pose.pose.orientation, axis_angle_to_quaternion([0, 0, 1], math.pi))
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
        return self.Action(cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms)
