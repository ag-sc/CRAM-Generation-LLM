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
            MoveTCPMotion(bowl_pose_in_gripper, self.arm).resolve().perform()
            MoveGripperMotion(self.grasp, self.arm).resolve().perform()
            for i in np.arange(0, 2 * math.pi, 0.1):
                x = 0.1 * math.cos(i)
                y = 0.1 * math.sin(i)
                z = 0.1 * i
                mix_pose = Pose([x, y, z], bowl_pose_in_gripper.pose.orientation, frame=bowl_pose_in_gripper.frame)
                MoveTCPMotion(mix_pose, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description = object_bowl_description
        self.arms = arms
        self.grasps = grasps
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if (isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) or isinstance(self.object_bowl_description, ObjectPart.Object)) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
