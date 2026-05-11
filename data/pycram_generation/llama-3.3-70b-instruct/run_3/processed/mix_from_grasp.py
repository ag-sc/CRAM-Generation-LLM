class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        grasp: str
        @with_tree
        def perform(self) -> None:
            bowl_pose = self.object_bowl_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)
            object_pose_in_gripper = lt.transform_pose(bowl_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            radius = 0.1
            for i in range(36):
                angle = i * math.pi / 18
                pose = Pose([object_pose_in_gripper.pose.position.x + radius * math.cos(angle), 
                            object_pose_in_gripper.pose.position.y + radius * math.sin(angle), 
                            object_pose_in_gripper.pose.position.z], 
                           axis_angle_to_quaternion([0, 0, angle]))
                MoveTCPMotion(pose, self.arm, allow_gripper_collision=True).resolve().perform()
                time.sleep(0.1)
                radius += 0.001
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description = object_bowl_description
        self.arms = arms
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if (isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) or isinstance(self.object_bowl_description, ObjectPart.Object)) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.arms[0])
