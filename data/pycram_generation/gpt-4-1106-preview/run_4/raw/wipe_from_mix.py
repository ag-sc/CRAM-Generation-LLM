
class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_description: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str

        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)

        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_cloth_description.data_copy()
            cloth = self.object_cloth_description.bullet_world_object

            def generate_zigzag(center_pose, length, width, gap):
                zigzag_poses = []
                half_length = length / 2
                half_width = width / 2
                num_strips = int(math.ceil(width / gap))
                for i in range(num_strips):
                    for direction in [1, -1]:
                        strip_pose = center_pose.copy()
                        strip_pose.pose.position.x += direction * half_length * (-1 if i % 2 == 0 else 1)
                        strip_pose.pose.position.y += half_width - i * gap
                        zigzag_poses.append(strip_pose)
                return zigzag_poses

            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                zigzag_poses = generate_zigzag(wipe_location, length, width, 0.1)
                for zigzag_pose in zigzag_poses:
                    adjusted_wipe_pose = zigzag_pose.copy()
                    MoveTCPMotion(adjusted_wipe_pose, self.arm).resolve().perform()

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
