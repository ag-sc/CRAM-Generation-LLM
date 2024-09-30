class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]
        @with_tree
        def perform(self) -> None:
            PickUpAction(self.object_cloth, self.arms, ["grasp"]).resolve().perform()
            for location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                for i in range(int(length/0.1)):
                    MoveTCPMotion(Pose([location.position[0] + i*0.1, location.position[1], location.position[2]], location.orientation), self.arms[0]).resolve().perform()
                    MoveTCPMotion(Pose([location.position[0] + i*0.1, location.position[1] + width, location.position[2]], location.orientation), self.arms[0]).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_cloth = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth, self.wipe_locations, self.lengths, self.widths, self.arms)
