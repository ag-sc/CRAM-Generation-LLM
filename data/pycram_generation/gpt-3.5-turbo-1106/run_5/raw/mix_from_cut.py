
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
            for i in range(10):
                bowl_pose.pose.position.x += 0.05 * math.cos(i * math.pi / 10)
                bowl_pose.pose.position.y += 0.05 * math.sin(i * math.pi / 10)
                MoveTCPMotion(bowl_pose, self.arm).resolve().perform()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
