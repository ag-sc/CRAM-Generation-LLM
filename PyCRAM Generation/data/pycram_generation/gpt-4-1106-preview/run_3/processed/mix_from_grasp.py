class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        grasp: str
        @with_tree
        def perform(self) -> None:
            bowl_pose = self.object_bowl_desig.bullet_world_object.get_pose() if isinstance(self.object_bowl_desig, ObjectDesignatorDescription.Object) else self.object_bowl_desig.part_pose
            lt = LocalTransformer()
            tool_frame = robot_description.get_tool_frame(self.arm)
            bowl_pose_in_tool = lt.transform_pose(bowl_pose, BulletWorld.robot.get_link_tf_frame(tool_frame))
            center_of_bowl = bowl_pose_in_tool.pose.position
            radius = 0.05  
            for angle in np.linspace(0, 2 * math.pi, num=36):  
                x = center_of_bowl.x + radius * math.cos(angle)
                y = center_of_bowl.y + radius * math.sin(angle)
                z = center_of_bowl.z
                radius += 0.001  
                mixing_pose = Pose([x, y, z], bowl_pose_in_tool.pose.orientation, bowl_pose_in_tool.frame)
                MoveTCPMotion(mixing_pose, self.arm).resolve().perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
