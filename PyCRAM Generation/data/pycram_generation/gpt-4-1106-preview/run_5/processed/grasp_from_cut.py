class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        @with_tree
        def perform(self) -> None:
            object = self.object_designator.bullet_world_object
            oTm = object.get_pose()
            pre_grasp_pose = oTm.copy()
            pre_grasp_pose.pose.position.z -= 0.1  
            MoveTCPMotion(pre_grasp_pose, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
            MoveTCPMotion(oTm, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_designator_description = object_designator_description
        self.arms = arms
    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, (ObjectDesignatorDescription.Object, ObjectPart.Object)) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0])