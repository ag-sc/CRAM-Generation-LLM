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
            if isinstance(self.object_cloth_desig, ObjectPart.Object):
                cloth_pose = self.object_cloth_desig.part_pose
            else:
                cloth_pose = self.object_cloth_desig.bullet_world_object.get_pose()
            PickUpAction(self.object_cloth_desig, [self.arm], []).resolve().perform()
            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                num_strips = math.ceil(length / 0.1)
                strip_length = width
                for i in range(num_strips):
                    start_x = wipe_location.position.x - (length / 2) + (i * 0.1)
                    end_x = start_x
                    start_y = wipe_location.position.y - (strip_length / 2)
                    end_y = wipe_location.position.y + (strip_length / 2)
                    start_pose = Pose([start_x, start_y, wipe_location.position.z], wipe_location.orientation, wipe_location.frame)
                    MoveTCPMotion(start_pose, self.arm).resolve().perform()
                    end_pose = Pose([end_x, end_y, wipe_location.position.z], wipe_location.orientation, wipe_location.frame)
                    MoveTCPMotion(end_pose, self.arm).resolve().perform()
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
