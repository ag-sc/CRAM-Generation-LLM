class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        @with_tree
        def perform(self) -> None:
            if isinstance(self.object_bowl_desig, ObjectPart.Object):
                object_bowl_pose = self.object_bowl_desig.part_pose
            else:
                object_bowl_pose = self.object_bowl_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)
            object_bowl_pose_in_gripper = lt.transform_pose(object_bowl_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            MoveTCPMotion(object_bowl_pose_in_gripper, self.arm).resolve().perform()
            for _ in range(5):
                object_bowl_pose_in_gripper.pose.position.x += 0.05
                MoveTCPMotion(object_bowl_pose_in_gripper, self.arm).resolve().perform()
                object_bowl_pose_in_gripper.pose.position.x -= 0.05
                MoveTCPMotion(object_bowl_pose_in_gripper, self.arm).resolve().perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_bowl_description
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if (isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) or isinstance(self.object_bowl_description, ObjectPart.Object)) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0])
