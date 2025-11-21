class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            pre_grasp_pose = Pose(position=[self.object_designator.pose.position[0], self.object_designator.pose.position[1], self.object_designator.pose.position[2] - 0.1], frame="map")
            MoveTCPMotion.Action(target=pre_grasp_pose, arm=self.arm).perform()
            MoveGripperMotion.Action(motion="open", gripper=self.arm).perform()
            MoveTCPMotion.Action(target=self.object_designator.pose, arm=self.arm).perform()
            MoveGripperMotion.Action(motion="close", gripper=self.arm).perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms
    def ground(self) -> Action:
        obj_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(obj_desig, self.arms[0])
