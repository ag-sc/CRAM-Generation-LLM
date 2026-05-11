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

            def generate_cut_pose(pose, upward_increment, radial_increment, angle_increment, steps, slice_thickness, technique):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                cut_poses = []

                if technique == 'halving':
                    for t in range(2):
                        tmp_pose = pose.copy()
                        x = x_start
                        y = y_start + (t * dim[1]) / 2
                        z = z_start

                        tmp_pose.pose.position.x += x
                        tmp_pose.pose.position.y += y
                        tmp_pose.pose.position.z += z

                        cutTm = object.local_transformer.transform_pose(tmp_pose, "map")
                        cut_poses.append(cutTm)
                        BulletWorld.current_bullet_world.add_vis_axis(cutTm)

                elif technique =='slicing':
                    for t in range(int(dim[1] / slice_thickness)):
                        tmp_pose = pose.copy()
                        x = x_start
                        y = y_start + (t * slice_thickness)
                        z = z_start

                        tmp_pose.pose.position.x += x
                        tmp_pose.pose.position.y += y
                        tmp_pose.pose.position.z += z

                        cutTm = object.local_transformer.transform_pose(tmp_pose, "map")
                        cut_poses.append(cutTm)
                        BulletWorld.current_bullet_world.add_vis_axis(cutTm)

                return cut_poses

            cut_poses = generate_cut_pose(object_pose, 0.001, 0.0035, math.radians(30), 10, self.slice_thickness, self.technique)

            BulletWorld.current_bullet_world.remove_vis_axis()

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
        self.object_designator_description = object_designator_description
        self.arms = arms
        self.grasps = grasps
        self.techniques = techniques
        self.slice_thicknesses = slice_thicknesses

    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
