
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
                # calculate the number of strips needed for the given length and width with a 10 cm gap
                num_strips = math.ceil(length / 0.1)
                strip_length = width

                # perform the zigzag pattern
                for i in range(num_strips):
                    # calculate start and end points of the strip
                    start_x = wipe_location.position.x - (length / 2) + (i * 0.1)
                    end_x = start_x
                    start_y = wipe_location.position.y - (strip_length / 2)
                    end_y = wipe_location.position.y + (strip_length / 2)

                    # move to start of the strip
                    start_pose = Pose([start_x, start_y, wipe_location.position.z], wipe_location.orientation, wipe_location.frame)
                    MoveTCPMotion(start_pose, self.arm).resolve().perform()

                    # wipe the strip
                    end_pose = Pose([end_x, end_y, wipe_location.position.z], wipe_location.orientation, wipe_location.frame)
                    MoveTCPMotion(end_pose, self.arm).resolve().perform()

            # place the cloth back
            PlaceAction(self.object_cloth_desig, [cloth_pose], [self.arm]).resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description = object_cloth_description
        self.wipe_locations = wipe_locations
        self.lengths = lengths
        self.widths = widths
        self.arms = arms

    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if (isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) or isinstance(self.object_cloth_description, ObjectPart.Object)) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
