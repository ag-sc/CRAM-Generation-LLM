class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_designator.data_copy()
            object = self.object_designator.bullet_world_object
            obj_dim = object.get_object_dimensions()
            dim = [max(obj_dim[0], obj_dim[1]), min(obj_dim[0], obj_dim[1]), obj_dim[2]]
            obj_height = dim[2]
            oTm = object.get_pose()
            object_pose = object.local_transformer.transform_to_object_frame(oTm, object)
            def generate_slices(pose, slice_thickness, steps):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                slice_poses = []
                for t in range(steps):
                    tmp_pose = pose.copy()
                    x = x_start + slice_thickness * t
                    tmp_pose.pose.position.x += x
                    sliceTm = object.local_transformer.transform_pose(tmp_pose, "map")
                    slice_poses.append(sliceTm)
                    BulletWorld.current_bullet_world.add_vis_axis(sliceTm)
                return slice_poses
            if self.technique == "halving":
                steps = 1
            elif self.technique == "slicing":
                steps = int(dim[0] / self.slice_thickness)
            slice_poses = generate_slices(object_pose, self.slice_thickness, steps)
            BulletWorld.current_bullet_world.remove_vis_axis()
            for slice_pose in slice_poses:
                oriR = axis_angle_to_quaternion([1, 0, 0], 180)
                ori = multiply_quaternions([slice_pose.orientation.x, slice_pose.orientation.y, slice_pose.orientation.z, slice_pose.orientation.w], oriR)
                adjusted_slice_pose = slice_pose.copy()
                adjusted_slice_pose.orientation.x = ori[0]
                adjusted_slice_pose.orientation.y = ori[1]
                adjusted_slice_pose.orientation.z = ori[2]
                adjusted_slice_pose.orientation.w = ori[3]
                lift_pose = adjusted_slice_pose.copy()
                lift_pose.pose.position.z += (obj_height + 0.08)
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses
    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
