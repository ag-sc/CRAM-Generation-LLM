class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        def perform(self) -> None:
            bowl = self.object_bowl_designator.bullet_world_object
            bowl_pose = bowl.get_pose()
            bowl_dim = bowl.get_object_dimensions()
            radius = min(bowl_dim[0], bowl_dim[1]) / 2
            height = bowl_dim[2]
            grasp_orientation = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            num_spirals = 3
            num_points_per_spiral = 10
            spiral_increment = radius / num_spirals
            for i in range(num_spirals):
                current_radius = spiral_increment * (i + 1)
                for j in range(num_points_per_spiral):
                    angle = (2 * math.pi / num_points_per_spiral) * j
                    x = current_radius * math.cos(angle)
                    y = current_radius * math.sin(angle)
                    z = height / 2
                    mix_pose = Pose([bowl_pose.position.x + x, bowl_pose.position.y + y, bowl_pose.position.z + z], grasp_orientation, frame="map")
                    MoveTCPMotion(mix_pose, self.arm).resolve().perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
