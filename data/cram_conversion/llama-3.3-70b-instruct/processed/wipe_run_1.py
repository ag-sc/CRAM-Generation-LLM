class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_description: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]
        @with_tree
        def perform(self) -> None:
            cloth_grasp_pose = Pose(position=[0, 0, 0.1], orientation=[0, 0, 0, 1])
            MoveGripperMotion('open', 'left').resolve().perform()
            PickUpAction(self.object_cloth_description, ['left'], ['side'], resolver=None).resolve().perform()
            MoveGripperMotion('close', 'left').resolve().perform()
            for i, location in enumerate(self.wipe_locations):
                MoveTCPMotion(location, 'left').resolve().perform()
                for j in range(int(self.lengths[i] / 0.1)):
                    if j % 2 == 0:
                        MoveTCPMotion(Pose(position=[location.position[0] + j * 0.1, location.position[1], location.position[2]], orientation=location.orientation), 'left').resolve().perform()
                    else:
                        MoveTCPMotion(Pose(position=[location.position[0] + j * 0.1, location.position[1] + self.widths[i], location.position[2]], orientation=location.orientation), 'left').resolve().perform()
            MoveGripperMotion('open', 'left').resolve().perform()
            PlaceAction(self.object_cloth_description, [Pose(position=[0, 0, 0.1], orientation=[0, 0, 0, 1])], ['left'], resolver=None).resolve().perform()
            MoveGripperMotion('close', 'left').resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description = object_cloth_description
        self.wipe_locations = wipe_locations
        self.lengths = lengths
        self.widths = widths
        self.arms = arms
    def ground(self) -> Action:
        object_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_desig, self.wipe_locations, self.lengths, self.widths, self.arms)
