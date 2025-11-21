class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            pre_grasp_pose = Pose(self.object_designator.pose.position - np.array([0, 0, 0.1]), self.object_designator.pose.orientation)
            MoveTCPMotion.Action(pre_grasp_pose, self.arm).perform()
            MoveGripperMotion.Action("open", self.arm).perform()
            MoveTCPMotion.Action(self.object_designator.pose, self.arm).perform()
            MoveGripperMotion.Action("close", self.arm).perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms
    def ground(self) -> Action:
        obj_desig = self.object_description if isinstance(self.object_description, (ObjectDesignatorDescription.Object, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(obj_desig, self.arms[0])
