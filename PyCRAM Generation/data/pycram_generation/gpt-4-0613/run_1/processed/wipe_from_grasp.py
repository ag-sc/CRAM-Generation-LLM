class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        cloth_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        wipe_location: Pose
        length: float
        width: float
        arm: str
        @with_tree
        def perform(self) -> None:
            if isinstance(self.cloth_desig, ObjectPart.Object):
                cloth_pose = self.cloth_desig.part_pose
            else:
                cloth_pose = self.cloth_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)
            cloth_pose_in_gripper = lt.transform_pose(cloth_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            MoveTCPMotion(cloth_pose, self.arm, allow_gripper_collision=True).resolve().perform()
            MoveGripperMotion("close", self.arm, allow_gripper_collision=True).resolve().perform()
            start_point = self.wipe_location.copy()
            start_point.pose.position.x -= self.length / 2
            start_point.pose.position.y -= self.width / 2
            end_point = start_point.copy()
            end_point.pose.position.x += self.length
            direction = 1
            while start_point.pose.position.y <= self.wipe_location.pose.position.y + self.width / 2:
                MoveTCPMotion(start_point, self.arm).resolve().perform()
                MoveTCPMotion(end_point, self.arm).resolve().perform()
                start_point.pose.position.y += 0.1
                end_point.pose.position.y += 0.1
                start_point, end_point = end_point, start_point
                direction *= -1
            MoveGripperMotion("open", self.arm).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description = object_cloth_description
        self.wipe_locations = wipe_locations
        self.lengths = lengths
        self.widths = widths
        self.arms = arms
    def ground(self) -> Action:
        cloth_desig = self.object_cloth_description if (isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) or isinstance(self.object_cloth_description, ObjectPart.Object)) else self.object_cloth_description.resolve()
        return self.Action(cloth_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
