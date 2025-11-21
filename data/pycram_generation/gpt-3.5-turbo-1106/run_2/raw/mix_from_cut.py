
class MixAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_bowl: ObjectDesignatorDescription.Object
        arm: str
        grasp: str

        def perform(self):
            bowl = self.object_bowl.bullet_world_object
            bowl_pose = bowl.get_pose()
            bowl_position = bowl_pose.position
            bowl_radius = 0.5  # Assuming a radius of 0.5 for the bowl
            num_spirals = 5  # Number of spirals for mixing motion
            spiral_height = 0.1  # Height of each spiral layer
            spiral_radius = 0.2  # Radius of the spiral motion

            for i in range(num_spirals):
                angle = i * 2 * math.pi / num_spirals
                mix_pose = Pose(
                    position=[bowl_position.x + spiral_radius * math.cos(angle),
                              bowl_position.y + spiral_radius * math.sin(angle),
                              bowl_position.z + i * spiral_height],
                    orientation=[0, 0, math.sin(angle / 2), math.cos(angle / 2)]
                )
                MoveTCPMotion(mix_pose, self.arm).resolve().perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
