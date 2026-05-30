class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        @with_tree
        def perform(self) -> None:
            object_pose = self.object_designator.bullet_world_object.get_pose()
            pre_grasp_pose = object_pose.copy()
            pre_grasp_pose.pose.position.x -= 0.1
            MoveTCPMotion(pre_grasp_pose, self.arm).resolve().perform()
            MoveGripperMotion('open', self.arm).resolve().perform()
            MoveTCPMotion(object_pose, self.arm).resolve().perform()
            MoveGripperMotion('close', self.arm).resolve().perform()

    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super(GraspAction, self).__init__(resolver)
        self.object_description = object_description
        self.arms = arms

    def __iter__(self):
        for arm in self.arms:
            yield self.Action(self.object_description, arm)

    def ground(self) -> Action:
        return next(iter(self))