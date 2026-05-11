class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        @with_tree
        def perform(self) -> None:
            ParkArmsAction.Action(Arms.BOTH).perform()
            pre_grasp_pose = Pose(position=[self.object_designator.position[0] - 0.1, self.object_designator.position[1], self.object_designator.position[2]], orientation=self.object_designator.orientation)
            MoveTCPMotion.Action(pre_grasp_pose, self.arm).perform()
            MoveGripperMotion.Action("open", self.arm).perform()
            MoveTCPMotion.Action(self.object_designator, self.arm).perform()
            MoveGripperMotion.Action("close", self.arm).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms
    def ground(self) -> Action:
        obj_desig = self.object_description if isinstance(self.object_description, (ObjectDesignatorDescription.Object, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(obj_desig, self.arms[0])
