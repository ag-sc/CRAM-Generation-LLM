
class MixAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str

        def perform(self) -> None:
            self.object_bowl_at_execution = self.object_bowl_designator.data_copy()
            grasp_orientation = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            bowl = self.object_bowl_designator.bullet_world_object
            bowl_pose = bowl.get_pose()
            bowl_dimensions = bowl.get_object_dimensions()
            bowl_radius = min(bowl_dimensions[0], bowl_dimensions[1]) / 2

            num_spirals = 3
            num_points_per_spiral = 10
            spiral_increment = bowl_radius / num_spirals
            current_radius = spiral_increment

            for spiral in range(num_spirals):
                angle_step = 2 * math.pi / num_points_per_spiral
                for step in range(num_points_per_spiral):
                    angle = step * angle_step
                    x_offset = current_radius * math.cos(angle)
                    y_offset = current_radius * math.sin(angle)
                    mix_pose = Pose([bowl_pose.position.x + x_offset, bowl_pose.position.y + y_offset, bowl_pose.position.z], grasp_orientation, frame="map")
                    MoveTCPMotion(mix_pose, self.arm).resolve().perform()
                current_radius += spiral_increment

            # Lift the tool after mixing
            lift_pose = Pose([bowl_pose.position.x, bowl_pose.position.y, bowl_pose.position.z + 0.1], grasp_orientation, frame="map")
            MoveTCPMotion(lift_pose, self.arm).resolve().perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
