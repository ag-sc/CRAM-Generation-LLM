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
            wipe_pose = self.wipe_location
            length = self.length
            width = self.width
            arm = self.arm

            def generate_zigzag(pose, length, width, gap, steps):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                zigzag_poses = []

                for t in range(2 * steps):
                    tmp_pose = pose.copy()

                    x = x_start + (t % 2) * width + (t // 2) * gap
                    y = y_start + (length / steps) * (t // 2)
                    z = z_start

                    tmp_pose.pose.position.x = x
                    tmp_pose.pose.position.y = y
                    tmp_pose.pose.position.z = z

                    zigzagTm = cloth.local_transformer.transform_pose(tmp_pose, "map")
                    zigzag_poses.append(zigzagTm)
                    BulletWorld.current_bullet_world.add_vis_axis(zigzagTm)

                return zigzag_poses

            zigzag_poses = generate_zigzag(wipe_pose, length, width, 0.1, 10)

            BulletWorld.current_bullet_world.remove_vis_axis()
            for zigzag_pose in zigzag_poses:
                MoveTCPMotion(zigzag_pose, arm).resolve().perform()

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

    def __iter__(self):
        for object_, wipe_location, length, width, arm in itertools.product(iter(self.object_cloth_description), 
                                                     self.wipe_locations, self.lengths, self.widths, self.arms):
            yield self.Action(object_, wipe_location, length, width, arm)
