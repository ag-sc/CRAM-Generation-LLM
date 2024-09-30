class MixAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        def perform(self) -> None:
            bowl = self.object_bowl_designator.bullet_world_object
            bowl_pose = bowl.get_pose()
            bowl_pose.pose.position.z += 0.1
            MoveTCPMotion(bowl_pose, self.arm).resolve().perform()
            num_spirals = 5
            spiral_radius = 0.05
            spiral_height = 0.02
            spiral_angle_increment = 0.2
            for i in range(num_spirals):
                spiral_pose = bowl_pose.copy()
                spiral_pose.pose.position.x += spiral_radius * math.cos(i * spiral_angle_increment)
                spiral_pose.pose.position.y += spiral_radius * math.sin(i * spiral_angle_increment)
                spiral_pose.pose.position.z += i * spiral_height
                MoveTCPMotion(spiral_pose, self.arm).resolve().perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
