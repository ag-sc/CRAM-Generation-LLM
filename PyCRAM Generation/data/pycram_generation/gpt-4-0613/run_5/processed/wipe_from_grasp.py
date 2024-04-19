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
            MoveTCPMotion(cloth_pose, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()
            wipe_start = self.wipe_location.copy()
            wipe_start.pose.position.x -= self.length / 2
            wipe_start.pose.position.y -= self.width / 2
            wipe_end = wipe_start.copy()
            wipe_end.pose.position.x += self.length
            direction = 1
            while wipe_start.pose.position.y <= self.wipe_location.pose.position.y + self.width / 2:
                MoveTCPMotion(wipe_start, self.arm).resolve().perform()
                MoveTCPMotion(wipe_end, self.arm).resolve().perform()
                wipe_start.pose.position.y += 0.1
                wipe_end.pose.position.y += 0.1
                wipe_start, wipe_end = wipe_end, wipe_start
                direction *= -1
            MoveGripperMotion("open", self.arm).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        cloth_desig = self.object_cloth_description if (isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) or isinstance(self.object_cloth_description, ObjectPart.Object)) else self.object_cloth_description.resolve()
        return self.Action(cloth_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
