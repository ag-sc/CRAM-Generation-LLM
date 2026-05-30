class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)
        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_source.data_copy()
            source = self.object_source.bullet_world_object
            container = self.object_container.bullet_world_object
            container_pose = container.get_pose()
            source_pose = source.get_pose()
            target_pose = container_pose.copy()
            target_pose.pose.position.z = container_pose.pose.position.z + 0.2
            target_pose.pose.orientation = multiply_quaternions([0, 0, 0, 1], axis_angle_to_quaternion([0, 1, 0], math.pi / 2))
            MoveTCPMotion(target_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            MoveTCPMotion(source_pose, self.arm).resolve().perform()
        def to_sql(self) -> ORMPourAction:
            return ORMPourAction(self.arm)
        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action
    def __init__(self, object_source_description: ObjectDesignatorDescription, object_container_description: ObjectDesignatorDescription, arms: List[str], durations: List[float], resolver=None):
        super(PourAction, self).__init__(resolver)
        self.object_source_description: ObjectDesignatorDescription = object_source_description
        self.object_container_description: ObjectDesignatorDescription = object_container_description
        self.arms: List[str] = arms
        self.d