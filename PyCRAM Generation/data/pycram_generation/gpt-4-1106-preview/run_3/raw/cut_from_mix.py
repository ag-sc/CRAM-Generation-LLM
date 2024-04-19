
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
            oTm = object.get_pose()
            object_pose = object.local_transformer.transform_to_object_frame(oTm, object)

            def generate_cut_poses(pose, slice_thickness, technique):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                cut_poses = []
                if technique == 'halving':
                    cut_pose = pose.copy()
                    cut_pose.pose.position.z += obj_dim[2] / 2
                    cut_poses.append(cut_pose)
                elif technique == 'slicing':
                    num_slices = int(obj_dim[0] / slice_thickness)
                    for i in range(num_slices):
                        cut_pose = pose.copy()
                        cut_pose.pose.position.x = x_start + (i * slice_thickness)
                        cut_pose.pose.position.z += obj_dim[2] / 2
                        cut_poses.append(cut_pose)
                return cut_poses

            cut_poses = generate_cut_poses(object_pose, self.slice_thickness, self.technique)

            for cut_pose in cut_poses:
                oriR = axis_angle_to_quaternion([0, 1, 0], 90)
                ori = multiply_quaternions([cut_pose.orientation.x, cut_pose.orientation.y, cut_pose.orientation.z, cut_pose.orientation.w], oriR)
                adjusted_cut_pose = cut_pose.copy()
                adjusted_cut_pose.orientation.x = ori[0]
                adjusted_cut_pose.orientation.y = ori[1]
                adjusted_cut_pose.orientation.z = ori[2]
                adjusted_cut_pose.orientation.w = ori[3]

                lift_pose = adjusted_cut_pose.copy()
                lift_pose.pose.position.z += 0.05
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
