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
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)
            cloth_pose = self.object_cloth_desig.bullet_world_object.get_pose()
            cloth_pose_in_gripper = lt.transform_pose(cloth_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            MoveTCPMotion(cloth_pose_in_gripper, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm, allow_gripper_collision=True).resolve().perform()
            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                num_strips = math.ceil(length / 0.1)
                for i in range(num_strips):
                    start_x = wipe_location.position.x - length / 2 + i * 0.1
                    end_x = start_x + length
                    y = wipe_location.position.y - width / 2 if i % 2 == 0 else wipe_location.position.y + width / 2
                    start_pose = Pose([start_x, y, wipe_location.position.z], wipe_location.orientation, wipe_location.frame)
                    end_pose = Pose([end_x, y, wipe_location.position.z], wipe_location.orientation, wipe_location.frame)
                    MoveTCPMotion(start_pose, self.arm).resolve().perform()
                    MoveTCPMotion(end_pose, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description = object_cloth_description
        self.wipe_locations = wipe_locations
        self.lengths = lengths
        self.widths = widths
        self.arms = arms
    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
