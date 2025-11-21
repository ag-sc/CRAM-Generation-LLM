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
                zigzag_poses = []
                for i in range(int(length / 0.1) + 1):
                    start_x = wipe_location.pose.position.x - length / 2 + i * 0.1
                    end_x = start_x + length
                    y = wipe_location.pose.position.y - width / 2 if i % 2 == 0 else wipe_location.pose.position.y + width / 2
                    z = wipe_location.pose.position.z
                    zigzag_poses.append(Pose([start_x, y, z], wipe_location.pose.orientation))
                    zigzag_poses.append(Pose([end_x, y, z], wipe_location.pose.orientation))
                for pose in zigzag_poses:
                    MoveTCPMotion(pose, self.arm).resolve().perform()
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
