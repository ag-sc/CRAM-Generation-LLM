class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)
        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_cloth.data_copy()
            cloth = self.object_cloth.bullet_world_object
            cloth_dim = cloth.get_object_dimensions()
            cloth_length = max(cloth_dim[0], cloth_dim[1])
            strip_gap = 0.1
            num_strips = int(self.length // strip_gap)
            start_offset = -self.length / 2 + strip_gap / 2
            strip_coordinates = [start_offset + i * strip_gap for i in range(num_strips)]
            wipe_poses = []
            for x in strip_coordinates:
                tmp_pose = self.wipe_location.copy()
                tmp_pose.pose.position.x = x
                wTm = LocalTransformer.transform_pose(tmp_pose, "map")
                wipe_poses.append(wTm)
            for wipe_pose in wipe_poses:
                adjusted_wipe_pose = wipe_pose.copy()
                lift_pose = adjusted_wipe_pose.copy()
                lift_pose.pose.position.z += 2 * cloth_length
                BulletWorld.current_bullet_world.add_vis_axis(lift_pose)
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()
                BulletWorld.current_bullet_world.add_vis_axis(adjusted_wipe_pose)
                MoveTCPMotion(adjusted_wipe_pose, self.arm).resolve().perform()
                BulletWorld.current_bullet_world.add_vis_axis(lift_pose)
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()
                BulletWorld.current_bullet_world.remove_vis_axis()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_cloth = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
