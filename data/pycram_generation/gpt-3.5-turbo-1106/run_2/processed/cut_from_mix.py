class CutAction(ActionDesignatorDescription):
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
            obj_width = dim[0]
            obj_height = dim[2]
            oTm = object.get_pose()
            object_pose = object.local_transformer.transform_to_object_frame(oTm, object)
            def generate_vertical_slices(pose, upward_increment, radial_increment, steps):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                slice_poses = []
                for t in range(steps):
                    tmp_pose = pose.copy()
                    h = upward_increment * t
                    z = z_start + h
                    tmp_pose.pose.position.z += z
                    sliceTm = object.local_transformer.transform_pose(tmp_pose, "map")
                    slice_poses.append(sliceTm)
                    BulletWorld.current_bullet_world.add_vis_axis(sliceTm)
                return slice_poses
            if self.technique == "halving":
                slice_poses = generate_vertical_slices(object_pose, 0.001, 0, 2)
            elif self.technique == "slicing":
                slice_poses = generate_vertical_slices(object_pose, 0.001, self.slice_thickness / 2, int(obj_width / self.slice_thickness))
            BulletWorld.current_bullet_world.remove_vis_axis()
            for slice_pose in slice_poses:
                MoveTCPMotion(slice_pose, self.arm).resolve().perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses
    def ground(self) -> Action:
        object_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
