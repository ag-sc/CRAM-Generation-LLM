
class MixAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        grasp: str

        @with_tree
        def perform(self) -> None:
            if isinstance(self.object_bowl_desig, ObjectPart.Object):
                bowl_pose = self.object_bowl_desig.part_pose
            else:
                bowl_pose = self.object_bowl_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)

            bowl_pose_in_gripper = lt.transform_pose(bowl_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))

            pre_mix = bowl_pose_in_gripper.copy()
            pre_mix.pose.position.x -= 0.1

            MoveTCPMotion(pre_mix, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()

            for i in range(10):
                angle = i * (2 * math.pi / 10)
                dx = 0.1 * math.cos(angle)
                dy = 0.1 * math.sin(angle)
                mix_pose = pre_mix.copy()
                mix_pose.pose.position.x += dx
                mix_pose.pose.position.y += dy
                MoveTCPMotion(mix_pose, self.arm, allow_gripper_collision=True).resolve().perform()

            MoveGripperMotion("close", self.arm, allow_gripper_collision=True).resolve().perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description = object_bowl_description
        self.arms = arms
        self.grasps = grasps

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if (isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) or isinstance(self.object_bowl_description, ObjectPart.Object)) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
