class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str
        gap: float
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)

        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_cloth_designator.data_copy()
            cloth = self.object_cloth_designator.bullet_world_object
            for location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                oTm = location
                object_pose = oTm
                num_strips = int(length // 0.1)
                strip_poses = []
                for i in range(num_strips):
                    tmp_pose = object_pose.copy()
                    tmp_pose.pose.position.x = object_pose.pose.position.x + (i * 0.1)
                    sTm = tmp_pose
                    strip_poses.append(sTm)
                for strip_pose in strip_poses:
                    ori = [0, 0, 0, 1]
                    adjusted_strip_pose = strip_pose.copy()
                    adjusted_strip_pose.orientation.x = ori[0]
                    adjusted_strip_pose.orientation.y = ori[1]
                    adjusted_strip_pose.orientation.z = ori[2]
                    adjusted_strip_pose.orientation.w = ori[3]
                    lift_pose = adjusted_strip_pose.copy()
                    lift_pose.pose.position.z += 0.01
                    MoveTCPMotion(lift_pose, self.arm).resolve().perform()
                    MoveTCPMotion(adjusted_strip_pose, self.arm).resolve().perform()
                    lift_pose.pose.position.x += width
                    MoveTCPMotion(lift_pose, self.arm).resolve().perform()

        def to_sql(self) -> None:
            return None

        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            return None

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super(WipeAction, self).__init__(resolver)
        self.object_cloth_description: ObjectDesignatorDescription = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def __iter__(self):
        for object_, arm in itertools.product(iter(self.object_cloth_description), self.arms):
            yield self.Action(object_, self.wipe_locations, self.lengths, self.widths, arm, 0.1)

    def ground(self) -> Action:
        return next(iter(self))
