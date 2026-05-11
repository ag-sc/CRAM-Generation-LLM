class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_cloth_designator.data_copy()
            cloth = self.object_cloth_designator.bullet_world_object
            for location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                obj_dim = cloth.get_object_dimensions()
                dim = [max(obj_dim[0], obj_dim[1]), min(obj_dim[0], obj_dim[1]), obj_dim[2]]
                cloth_height = dim[2]
                oTm = cloth.get_pose()
                cloth_pose = cloth.local_transformer.transform_to_object_frame(oTm, cloth)
                def generate_zigzag(pose, length, width, gap, steps):
                    zigzag_poses = []
                    x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                    for t in range(steps):
                        tmp_pose = pose.copy()
                        x = x_start + (t % 2 == 0 and -width/2 or width/2)
                        y = y_start + t * gap
                        if t > 0 and t % 2 == 0:
                            y -= gap
                        z = z_start
                        tmp_pose.pose.position.x += x
                        tmp_pose.pose.position.y += y
                        tmp_pose.pose.position.z += z
                        zigzagTm = cloth.local_transformer.transform_pose(tmp_pose, "map")
                        zigzag_poses.append(zigzagTm)
                    return zigzag_poses
                zigzag_poses = generate_zigzag(location, length, width, 0.1, int(length/0.1))
                for zigzag_pose in zigzag_poses:
                    oriR = axis_angle_to_quaternion([1, 0, 0], 180)
                    ori = multiply_quaternions([zigzag_pose.orientation.x, zigzag_pose.orientation.y, zigzag_pose.orientation.z, zigzag_pose.orientation.w], oriR)
                    adjusted_wipe_pose = zigzag_pose.copy()
                    adjusted_wipe_pose.orientation.x = ori[0]
                    adjusted_wipe_pose.orientation.y = ori[1]
                    adjusted_wipe_pose.orientation.z = ori[2]
                    adjusted_wipe_pose.orientation.w = ori[3]
                    lift_pose = adjusted_wipe_pose.copy()
                    lift_pose.pose.position.z += (cloth_height + 0.08)
                    MoveTCPMotion(lift_pose, self.arm).resolve().perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description = object_cloth_description
        self.wipe_locations = wipe_locations
        self.lengths = lengths
        self.widths = widths
        self.arms = arms
    def ground(self) -> Action:
        object_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
