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
            def generate_vertical_slicing(pose, slice_thickness):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                slicing_poses = []
                for t in range(int(obj_dim[1] / slice_thickness)):
                    tmp_pose = pose.copy()
                    y = y_start + slice_thickness * t
                    tmp_pose.pose.position.y += y
                    slicingTm = object.local_transformer.transform_pose(tmp_pose, "map")
                    slicing_poses.append(slicingTm)
                    BulletWorld.current_bullet_world.add_vis_axis(slicingTm)
                return slicing_poses
            if self.technique == 'halving':
                slice_thickness = obj_dim[1] / 2
                slicing_poses = generate_vertical_slicing(object_pose, slice_thickness)
            elif self.technique == 'slicing':
                slicing_poses = generate_vertical_slicing(object_pose, self.slice_thickness)
            BulletWorld.current_bullet_world.remove_vis_axis()
            for slicing_pose in slicing_poses:
                oriR = axis_angle_to_quaternion([1, 0, 0], 180)
                ori = multiply_quaternions([slicing_pose.orientation.x, slicing_pose.orientation.y, slicing_pose.orientation.z, slicing_pose.orientation.w], oriR)
                adjusted_cut_pose = slicing_pose.copy()
                adjusted_cut_pose.orientation.x = ori[0]
                adjusted_cut_pose.orientation.y = ori[1]
                adjusted_cut_pose.orientation.z = ori[2]
                adjusted_cut_pose.orientation.w = ori[3]
                lift_pose = adjusted_cut_pose.copy()
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
