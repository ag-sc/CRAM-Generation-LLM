class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str
        @with_tree
        def perform(self) -> None:
            object_cloth_pose = self.object_cloth_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)
            object_cloth_pose_in_gripper = lt.transform_pose(object_cloth_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            MoveTCPMotion(object_cloth_pose_in_gripper, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()
            for i, location in enumerate(self.wipe_locations):
                length = self.lengths[i]
                width = self.widths[i]
                num_strips = int(length / 0.1)
                for j in range(num_strips):
                    strip_location = Pose(location.pose.position.x, location.pose.position.y + j * 0.1, location.pose.position.z, location.pose.orientation)
                    MoveTCPMotion(strip_location, self.arm, allow_gripper_collision=True).resolve().perform()
                    if j % 2 == 0:
                        MoveTCPMotion(Pose(location.pose.position.x + width, location.pose.position.y + j * 0.1, location.pose.position.z, location.pose.orientation), self.arm, allow_gripper_collision=True).resolve().perform()
                    else:
                        MoveTCPMotion(Pose(location.pose.position.x - width, location.pose.position.y + j * 0.1, location.pose.position.z, location.pose.orientation), self.arm, allow_gripper_collision=True).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description = object_cloth_description
        self.wipe_locations = wipe_locations
        self.lengths = lengths
        self.widths = widths
        self.arms = arms
    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if (isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) or isinstance(self.object_cloth_description, ObjectPart.Object)) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
