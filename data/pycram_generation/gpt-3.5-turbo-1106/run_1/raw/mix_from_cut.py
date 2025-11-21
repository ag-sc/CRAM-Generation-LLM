
class MixAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str

        def perform(self) -> None:
            bowl = self.object_bowl_designator.bullet_world_object
            bowl_pose = bowl.get_pose()
            bowl_position = bowl_pose.position
            bowl_radius = 0.5  # Assuming a default radius for the bowl

            num_spirals = 5
            num_points_per_spiral = 100
            spiral_radius = 0.1  # Assuming a default radius for the mixing motion

            for i in range(num_spirals):
                for j in range(num_points_per_spiral):
                    angle = 2 * math.pi * j / num_points_per_spiral
                    x = bowl_position.x + (bowl_radius + i * spiral_radius) * math.cos(angle)
                    y = bowl_position.y + (bowl_radius + i * spiral_radius) * math.sin(angle)
                    z = bowl_position.z  # Assuming the mixing motion is in the same plane as the bowl
                    mix_pose = Pose([x, y, z], bowl_pose.orientation)
                    MoveTCPMotion(mix_pose, self.arm).resolve().perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
