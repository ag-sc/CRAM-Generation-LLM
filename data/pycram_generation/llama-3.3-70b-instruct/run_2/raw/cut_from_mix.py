class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float

        @with_tree
        def perform(self) -> None:
            object = self.object_designator.bullet_world_object
            obj_dim = object.get_object_dimensions()
            dim = [max(obj_dim[0], obj_dim[1]), min(obj_dim[0], obj_dim[1]), obj_dim[2]]
            oTm = object.get_pose()
            object_pose = object.local_transformer.transform_to_object_frame(oTm, object)

            if self.technique == 'halving':
                start_offset = 0
                num_slices = 1
            else:
                num_slices = int(dim[0] // self.slice_thickness)
                start_offset = -dim[0] / 2 + self.slice_thickness / 2

            slice_coordinates = [start_offset + i * self.slice_thickness for i in range(num_slices)]

            slice_poses = []
            for x in slice_coordinates:
                tmp_pose = object_pose.copy()
                tmp_pose.pose.position.x = x
                sTm = object.local_transformer.transform_pose(tmp_pose, "map")
                slice_poses.append(sTm)

            for slice_pose in slice_poses:
                oriR = axis_angle_to_quaternion([0, 0, 1], 90)
                ori = multiply_quaternions([slice_pose.orientation.x, slice_pose.orientation.y,
                                            slice_pose.orientation.z, slice_pose.orientation.w], oriR)
                adjusted_slice_pose = slice_pose.copy()
                adjusted_slice_pose.orientation.x = ori[0]
                adjusted_slice_pose.orientation.y = ori[1]
                adjusted_slice_pose.orientation.z = ori[2]
                adjusted_slice_pose.orientation.w = ori[3]

                lift_pose = adjusted_slice_pose.copy()
                lift_pose.pose.position.z += dim[2] + 0.08
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()
                MoveTCPMotion(adjusted_slice_pose, self.arm).resolve().perform()
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()

        def to_sql(self) -> Base:
            return ORMCuttingAction(self.arm, self.grasp)

        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super(CutAction, self).__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        return self.Action(self.object_designator_description, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])

    def __iter__(self):
        for object_, arm, grasp, technique, slice_thickness in itertools.product(self.object_designator_description, 
                                                                     self.arms, self.grasps, self.techniques, self.slice_thicknesses):
            yield self.Action(object_, arm, grasp, technique, slice_thickness)
