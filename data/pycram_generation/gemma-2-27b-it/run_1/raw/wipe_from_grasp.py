class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str

        @with_tree
        def perform(self) -> None:
            MoveTCPMotion(self.wipe_locations[0], self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
            MoveTCPMotion(self.wipe_locations[0], self.arm, allow_gripper_collision=True).resolve().perform()
            MoveGripperMotion("close", self.arm, allow_gripper_collision=True).resolve().perform()
            for i in range(len(self.lengths)):
                for j in range(int(self.widths[i] / 0.1)):
                    MoveTCPMotion(self.wipe_locations[i].copy(), self.arm).resolve().perform()
                    MoveTCPMotion(self.wipe_locations[i].copy(), self.arm, allow_gripper_collision=True).resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        object_desig = self.object_cloth_description if (isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) or isinstance(self.object_cloth_description, ObjectPart.Object)) else