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
            gripper_name = robot_description.get_tool_frame(self.arm)
            lt = LocalTransformer()
            cloth_pose = self.object_cloth_desig.bullet_world_object.get_pose()
            cloth_pose_in_gripper = lt.transform_pose(cloth_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            pre_grasp_cloth = cloth_pose_in_gripper.copy()
            pre_grasp_cloth.pose.position.x -= 0.1
            MoveTCPMotion(pre_grasp_cloth, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
            MoveTCPMotion(cloth_pose, self.arm, allow_gripper_collision=True).resolve().perform()
            MoveGripperMotion("close", self.arm, allow_gripper_collision=True).resolve().perform()
            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                wipe_location_in_gripper = lt.transform_pose(wipe_location, BulletWorld.robot.get_link_tf_frame(gripper_name))
                num_strips = math.ceil(length / 0.1)
                for i in range(num_strips):
                    strip_pose = wipe_location_in_gripper.copy()
                    strip_pose.pose.position.x += (i * 0.1) if i % 2 == 0 else (length - (i * 0.1))
                    strip_pose.pose.position.y += 0 if i % 2 == 0 else width
                    MoveTCPMotion(strip_pose, self.arm).resolve().perform()
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
