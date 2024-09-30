
class WipeAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str

        @with_tree
        def perform(self) -> None:
            cloth = self.object_designator.bullet_world_object
            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                wipe_pose = wipe_location.copy()
                wipe_pose.pose.position.z += 0.02  # Lift the cloth slightly above the surface

                # Calculate the number of strips needed for the given length and gap
                num_strips = int(length / 0.1)
                strip_length = length / num_strips

                for i in range(num_strips):
                    # Calculate the starting point for the current strip
                    start_x = wipe_pose.pose.position.x - (length / 2) + (i * strip_length)
                    start_y = wipe_pose.pose.position.y - (width / 2)
                    end_y = start_y + width

                    # Zigzag pattern: alternate the direction for each strip
                    if i % 2 == 0:
                        y_coords = [start_y, end_y]
                    else:
                        y_coords = [end_y, start_y]

                    for y in y_coords:
                        # Set the position for the current end of the strip
                        strip_pose = wipe_pose.copy()
                        strip_pose.pose.position.x = start_x
                        strip_pose.pose.position.y = y

                        # Perform the wiping motion
                        MoveTCPMotion(strip_pose, self.arm).resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        object_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
