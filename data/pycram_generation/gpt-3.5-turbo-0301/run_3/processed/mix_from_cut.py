class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        @with_tree
        def perform(self) -> None:
            bowl = self.object_bowl_designator.bullet_world_object
            grasp = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            bowl_pose = bowl.get_pose()
            bowl_dim = bowl.get_object_dimensions()
            bowl_radius = bowl_dim[0] / 2
            bowl_height = bowl_dim[2]
            bowl_position = np.array([bowl_pose.pose.position.x, bowl_pose.pose.position.y, bowl_pose.pose.position.z])
            bowl_orientation = np.array([bowl_pose.pose.orientation.x, bowl_pose.pose.orientation.y, bowl_pose.pose.orientation.z, bowl_pose.pose.orientation.w])
            tool_position = np.array([0, 0, 0])
            tool_orientation = np.array([0, 0, 0, 1])
            angle = 0
            spiral_radius = bowl_radius / 2
            spiral_height = bowl_height / 2
            num_revolutions = 2
            num_steps = 20
            step_size = 0.05
            height_step_size = spiral_height / num_steps
            angle_step_size = 2 * math.pi / (num_steps * num_revolutions)
            tool_height = bowl_height / 2
            tool_height_step_size = height_step_size / 2
            tool_angle_step_size = angle_step_size / 2
            for i in range(num_revolutions * num_steps):
                tool_position[0] = bowl_position[0] + spiral_radius * math.cos(angle)
                tool_position[1] = bowl_position[1] + spiral_radius * math.sin(angle)
                tool_position[2] = bowl_position[2] + tool_height
                tool_orientation = multiply_quaternions([grasp[0], grasp[1], grasp[2], grasp[3]], [0, 0, math.sin(angle), math.cos(angle)])
                tool_pose = Pose(position=tool_position.tolist(), orientation=tool_orientation.tolist())
                MoveTCPMotion(tool_pose, self.arm).resolve().perform()
                angle += angle_step_size
                tool_height -= tool_height_step_size
                spiral_radius += step_size
                spiral_height -= height_step_size
                tool_angle_step_size = angle_step_size / 2
                tool_height_step_size = height_step_size / 2
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
