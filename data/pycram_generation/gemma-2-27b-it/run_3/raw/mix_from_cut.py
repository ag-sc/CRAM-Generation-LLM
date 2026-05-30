class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        
        def perform(self) -> None:
            pass

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super(MixAction, self).__init__(resolver)
        self.object_bowl_description: ObjectDesignatorDescription = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def __iter__(self):
        for object_, grasp, arm in itertools.product(iter(self.object_bowl_description), self.grasps, self.arms):
            yield self.Action(object_, arm, grasp)

    def ground(self) -> Action:
        return next(iter(self))