
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
                x_start = wipe_location.position.x - length / 2
                x_end = wipe_location.position.x + length / 2
                y_start = wipe_location.position.y - width / 2
                y_end = wipe_location.position.y + width / 2

                for x in np.arange(x_start, x_end, 0.1):
                    if x % 0.2 == 0:
                        y_range = np.arange(y_start, y_end, 0.1)
                    else:
                        y_range = np.arange(y_end, y_start, -0.1)

                    for y in y_range:
                        wipe_pose = Pose([x, y, cloth_pose.position.z], cloth_pose.orientation, cloth_pose.frame)
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
