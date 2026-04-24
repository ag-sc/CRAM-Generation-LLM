class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str
        @with_tree
        def perform(self) -> None:
            robot = BulletWorld.robot
            cloth = self.object_cloth_designator.bullet_world_object
            wipe_surface = self.wipe_location.bullet_world_object
            cloth_dim = cloth.get_object_dimensions()
            cloth_length = cloth_dim[0]
            cloth_width = cloth_dim[1]
            cloth_height = cloth_dim[2]
            wipe_dim = wipe_surface.get_object_dimensions()
            wipe_length = wipe_dim[0]
            wipe_width = wipe_dim[1]
            wipe_height = wipe_dim[2]
            oTm = wipe_surface.get_pose()
            wipe_pose = wipe_surface.local_transformer.transform_to_object_frame(oTm, wipe_surface)
            def generate_zigzag(pose, length, width, gap, steps):
                zigzag_poses = []
                for t in range(steps):
                    tmp_pose = pose.copy()
                    x = (t % 2) * width
                    y = (t // 2) * gap
                    tmp_pose.pose.position.x += x
                    tmp_pose.pose.position.y += y
                    zigzagTm = wipe_surface.local_transformer.transform_pose(tmp_pose, "map")
                    zigzag_poses.append(zigzagTm)
                    BulletWorld.current_bullet_world.add_vis_axis(zigzagTm)
                return zigzag_poses
            zigzag_poses = generate_zigzag(wipe_pose, length, width, 0.1, int(wipe_length // 0.1))
            BulletWorld.current_bullet_world.remove_vis_axis()
            for zigzag_pose in zigzag_poses:
                oriR = axis_angle_to_quaternion([1, 0, 0], 180)
                ori = multiply_quaternions([zigzag_pose.orientation.x, zigzag_pose.orientation.y,
                                            zigzag_pose.orientation.z, zigzag_pose.orientation.w], oriR)
                adjusted_zigzag_pose = zigzag_pose.copy()
                adjusted_zigzag_pose.orientation.x = ori[0]
                adjusted_zigzag_pose.orientation.y = ori[1]
                adjusted_zigzag_pose.orientation.z = ori[2]
                adjusted_zigzag_pose.orientation.w = ori[3]
                lift_pose = adjusted_zigzag_pose.copy()
                lift_pose.pose.position.z += (wipe_height + 0.08)
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()
                MoveTCPMotion(adjusted_zigzag_pose, self.arm).resolve().perform()
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()
        def to_sql(self) -> Base:
            return ORMWipeAction(self.arm)
        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super(WipeAction, self).__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        return self.Action(self.object_cloth_description.ground(), self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
