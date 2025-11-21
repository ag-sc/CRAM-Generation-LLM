
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

            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                # calculate the start and end points of the zigzag pattern
                start_point = wipe_location.copy()
                start_point.pose.position.x -= length / 2
                start_point.pose.position.y -= width / 2

                end_point = wipe_location.copy()
                end_point.pose.position.x += length / 2
                end_point.pose.position.y -= width / 2

                # perform the zigzag wiping pattern
                while start_point.pose.position.y < wipe_location.pose.position.y + width / 2:
                    # move to start point
                    MoveTCPMotion(start_point, self.arm).resolve().perform()
                    # move to end point
                    MoveTCPMotion(end_point, self.arm).resolve().perform()
                    # move the start and end points up by the gap distance for the next strip
                    start_point.pose.position.y += 0.1
                    end_point.pose.position.y += 0.1

            # place the cloth back
            PlaceAction(self.object_cloth_desig, [cloth_pose], [self.arm]).resolve().perform()

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
