
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
            # get pose of cloth to be used for wiping
            if isinstance(self.object_cloth_desig, ObjectPart.Object):
                cloth_pose = self.object_cloth_desig.part_pose
            else:
                cloth_pose = self.object_cloth_desig.bullet_world_object.get_pose()

            # pick up the cloth
            PickUpAction(self.object_cloth_desig, [self.arm], []).resolve().perform()

            # wipe each location
            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                # calculate the starting corner of the wipe area
                start_pose = wipe_location.copy()
                start_pose.pose.position.x -= length / 2
                start_pose.pose.position.y -= width / 2

                # perform the zigzag pattern
                for i in range(math.ceil(width / 0.1)):
                    # move to the start of the strip
                    strip_start_pose = start_pose.copy()
                    strip_start_pose.pose.position.y += i * 0.1
                    MoveTCPMotion(strip_start_pose, self.arm).resolve().perform()

                    # wipe the strip
                    strip_end_pose = strip_start_pose.copy()
                    strip_end_pose.pose.position.x += length
                    MoveTCPMotion(strip_end_pose, self.arm).resolve().perform()

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
