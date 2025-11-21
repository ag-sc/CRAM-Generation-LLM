
class WipeAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str

        def perform(self) -> None:
            cloth_object = self.object_cloth_designator.bullet_world_object
            cloth_pose = cloth_object.get_pose()

            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                for x in np.arange(-length/2, length/2, 0.1):
                    for y in np.arange(-width/2, width/2, 0.1):
                        wipe_pose = Pose([wipe_location.position[0] + x, wipe_location.position[1] + y, wipe_location.position[2]], wipe_location.orientation)
                        MoveTCPMotion(wipe_pose, self.arm).resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
