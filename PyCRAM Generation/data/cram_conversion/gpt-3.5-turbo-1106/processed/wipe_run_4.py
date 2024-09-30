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
            for arm in self.arms:
                for i in range(len(self.wipe_locations)):
                    current_pose = self.wipe_locations[i]
                    length = self.lengths[i]
                    width = self.widths[i]
                    while length > 0:
                        MoveTCPMotion(current_pose, arm).resolve().perform()
                        current_pose.position[0] += length
                        MoveTCPMotion(current_pose, arm).resolve().perform()
                        current_pose.position[1] += width
                        length -= 0.1
                    current_pose.position[1] -= width
                    MoveTCPMotion(current_pose, arm).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms)
