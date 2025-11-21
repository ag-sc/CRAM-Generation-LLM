
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

            def generate_cut_poses(pose, thickness, steps):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                cut_poses = []

                for t in range(steps):
                    tmp_pose = pose.copy()
                    x = x_start + thickness * t
                    tmp_pose.pose.position.x += x
                    cut_poses.append(tmp_pose)

                return cut_poses

            if self.technique == 'halving':
                steps = 1
            elif self.technique == 'slicing':
                steps = int(dim[0] / self.slice_thickness)

            cut_poses = generate_cut_poses(object_pose, self.slice_thickness, steps)

            for cut_pose in cut_poses:
                oriR = axis_angle_to_quaternion([1, 0, 0], 180)
                ori = multiply_quaternions([cut_pose.orientation.x, cut_pose.orientation.y, cut_pose.orientation.z, cut_pose.orientation.w], oriR)
                adjusted_cut_pose = cut_pose.copy()
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
