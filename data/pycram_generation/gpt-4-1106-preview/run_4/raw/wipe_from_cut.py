
class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str

        def perform(self) -> None:
            self.object_cloth_designator = self.object_cloth_designator.data_copy()
            cloth = self.object_cloth_designator.bullet_world_object
            cloth_pose = cloth.local_transformer.transform_to_object_frame(cloth.get_pose(), cloth)

            zigzag_pattern = []
            num_strips = int(self.length // 0.1)
            for i in range(num_strips):
                start_x = self.wipe_location.pose.position.x - self.length / 2
                start_y = self.wipe_location.pose.position.y - self.width / 2 if i % 2 == 0 else self.wipe_location.pose.position.y + self.width / 2
                end_y = self.wipe_location.pose.position.y + self.width / 2 if i % 2 == 0 else self.wipe_location.pose.position.y - self.width / 2
                zigzag_pattern.append(Pose([start_x, start_y, self.wipe_location.pose.position.z], self.wipe_location.pose.orientation))
                start_x += 0.1
                zigzag_pattern.append(Pose([start_x, end_y, self.wipe_location.pose.position.z], self.wipe_location.pose.orientation))

            for pose in zigzag_pattern:
                BulletWorld.current_bullet_world.add_vis_axis(pose)
                MoveTCPMotion(pose, self.arm).resolve().perform()
                BulletWorld.current_bullet_world.remove_vis_axis()

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
