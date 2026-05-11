class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str

        def __init__(self, object_designator, arm, resolver=None):
            self.object_designator = object_designator
            self.arm = arm

        @with_tree
        def perform(self) -> None:
            object = self.object_designator.bullet_world_object
            oTm = object.get_pose()
            object_pose = object.local_transformer.transform_to_object_frame(oTm, object)

            pre_grasp_pose = object_pose.copy()
            pre_grasp_pose.pose.position.x -= 0.1

            MoveTCPMotion(pre_grasp_pose, self.arm).resolve().perform()
            MoveGripperMotion('open', self.arm).resolve().perform()
            MoveTCPMotion(object_pose, self.arm).resolve().perform()
            MoveGripperMotion('close', self.arm).resolve().perform()

        def to_sql(self) -> None:
            return None

        def insert(self, session, **kwargs):
            return None

    def __init__(self, object_description, arms, resolver=None):
        super(GraspAction, self).__init__(resolver)
        self.object_description = object_description
        self.arms = arms

    def __iter__(self):
        for object_, arm in itertools.product(iter(self.object_description), self.arms):
            yield self.Action(object_, arm)

    def ground(self) -> Action:
        return next(iter(self))
