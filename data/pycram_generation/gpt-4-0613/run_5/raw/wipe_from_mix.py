
class WipeAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)

        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_designator.data_copy()
            object = self.object_designator.bullet_world_object

            def generate_zigzag(pose, length, width, gap):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                zigzag_poses = []
                direction = 1

                for i in np.arange(0, length, gap):
                    tmp_pose = pose.copy()
                    x = x_start + i
                    y = y_start + direction * (width / 2)
                    tmp_pose.pose.position.x += x
                    tmp_pose.pose.position.y += y
                    zigzagTm = object.local_transformer.transform_pose(tmp_pose, "map")
                    zigzag_poses.append(zigzagTm)
                    BulletWorld.current_bullet_world.add_vis_axis(zigzagTm)
                    direction *= -1

                return zigzag_poses

            zigzag_poses = generate_zigzag(self.wipe_location, self.length, self.width, 0.1)
            BulletWorld.current_bullet_world.remove_vis_axis()

            for zigzag_pose in zigzag_poses:
                MoveTCPMotion(zigzag_pose, self.arm).resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        object_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
