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
            tool_frame = robot_description.get_tool_frame(self.arm)
            bowl_pose_in_tool = lt.transform_pose(bowl_pose, BulletWorld.robot.get_link_tf_frame(tool_frame))
            radius_increment = 0.005
            angle_increment = math.radians(10)
            current_radius = 0.05
            current_angle = 0
            while current_radius <= 0.1:
                x_offset = current_radius * math.cos(current_angle)
                y_offset = current_radius * math.sin(current_angle)
                mixing_pose = bowl_pose_in_tool.copy()
                mixing_pose.pose.position.x += x_offset
                mixing_pose.pose.position.y += y_offset
                MoveTCPMotion(mixing_pose, self.arm).resolve().perform()
                current_angle += angle_increment
                if current_angle >= 2 * math.pi:
                    current_angle -= 2 * math.pi
                    current_radius += radius_increment
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
