
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
                for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                    # Move to the initial position
                    initial_pose = Pose(wipe_location.position, wipe_location.orientation)
                    MoveTCPMotion(initial_pose, arm).resolve().perform()

                    # Wipe in a zigzag pattern
                    for i in range(int(length / 0.1)):
                        # Calculate the new position
                        new_position = [wipe_location.position[0] + i * 0.1, wipe_location.position[1] + (width if i % 2 == 0 else 0), wipe_location.position[2]]
                        new_pose = Pose(new_position, wipe_location.orientation)

                        # Move to the new position
                        MoveTCPMotion(new_pose, arm).resolve().perform()

                    # Return to the initial position
                    MoveTCPMotion(initial_pose, arm).resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        object_cloth = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth, self.wipe_locations, self.lengths, self.widths, self.arms)
