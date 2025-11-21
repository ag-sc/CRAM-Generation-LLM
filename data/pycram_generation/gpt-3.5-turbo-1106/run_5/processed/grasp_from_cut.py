class GraspAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object]
        arm: str
        def perform(self) -> None:
            pre_grasp_pose = CostmapLocation(self.object_description, reachable_arm=self.arm, resolver=self.object_description.resolve).resolve()
            MoveTCPMotion(pre_grasp_pose, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
            object_pose = CostmapLocation(self.object_description, reachable_arm=self.arm, resolver=self.object_description.resolve).resolve()
            MoveTCPMotion(object_pose, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, (ObjectDesignatorDescription.Object, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0])
