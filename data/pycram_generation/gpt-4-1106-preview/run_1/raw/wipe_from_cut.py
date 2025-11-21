
class WipeAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_description: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str
        gap: float = 0.1

        @with_tree
        def perform(self) -> None:
            object_cloth = self.object_cloth_description.bullet_world_object
            cloth_pose = object_cloth.get_pose()
            wipe_center_pose = self.wipe_location

            num_strips = int(self.length // self.gap)
            start_offset_x = wipe_center_pose.pose.position.x - self.length / 2
            start_offset_y = wipe_center_pose.pose.position.y - self.width / 2

            for i in range(num_strips):
                x = start_offset_x + i * self.gap
                for j in range(2):
                    y = start_offset_y if j % 2 == 0 else start_offset_y + self.width
                    target_pose = wipe_center_pose.copy()
                    target_pose.pose.position.x = x
                    target_pose.pose.position.y = y
                    MoveTCPMotion(target_pose, self.arm).resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
