class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)
        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_cloth_designator.data_copy()
            cloth = self.object_cloth_designator.bullet_world_object
            cloth_dim = cloth.get_object_dimensions()
            cloth_pose = cloth.get_pose()
            num_strips = int(self.length // 0.1)
            strip_coordinates = [self.wipe_location.pose.position.x - self.length / 2 + i * 0.1 for i in range(num_strips)]
            for x in strip_coordinates:
                adjusted_wipe_pose = self.wipe_location.copy()
                adjusted_wipe_pose.pose.position.x = x
                adjusted_wipe_pose.pose.position.y -= self.width / 2
                MoveTCPMotion(adjusted_wipe_pose, self.arm).resolve().perform()
                adjusted_wipe_pose.pose.position.y += self.width
                MoveTCPMotion(adjusted_wipe_pose, self.arm).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
