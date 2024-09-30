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
            tool_position = np.array([bowl_position[0], bowl_position[1] + bowl_radius, bowl_position[2] + bowl_height])
            tool_orientation = np.array([0, 0, 0, 1])
            rotation_angle = 0
            mixing_radius = bowl_radius / 2
            mixing_height = bowl_height / 2
            num_revolutions = 2
            num_steps = 20
            step_size = 0.05
            height_step_size = mixing_height / num_steps
            angle_step_size = 2 * math.pi / (num_steps * num_revolutions)
            height = mixing_height
            angle = 0
            for i in range(num_steps * num_revolutions):
                x = mixing_radius * math.cos(angle)
                y = mixing_radius * math.sin(angle)
                z = height
                tool_position = np.array([bowl_position[0] + x, bowl_position[1] + y, bowl_position[2] + z])
                tool_orientation = multiply_quaternions([grasp[0], grasp[1], grasp[2], grasp[3]], [0, 0, math.sin(rotation_angle / 2), math.cos(rotation_angle / 2)])
                tool_pose = Pose(position=tool_position.tolist(), orientation=tool_orientation.tolist())
                MoveTCPMotion(tool_pose, self.arm).resolve().perform()
                angle += angle_step_size
                height -= height_step_size
                rotation_angle += 0.1
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
