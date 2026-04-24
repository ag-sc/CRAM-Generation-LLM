class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        @with_tree
        def perform(self) -> None:
            TransportAction.Action(self.object_source, self.arm, self.object_container.bullet_world_object.get_pose()).perform()
            object_source_pose = self.object_source.bullet_world_object.get_pose()
            object_container_pose = self.object_container.bullet_world_object.get_pose()
            pour_pose = Pose(position=[object_container_pose.position.x, object_container_pose.position.y, object_container_pose.position.z + 0.2],
                             orientation=axis_angle_to_quaternion([0, 0, 1], math.pi / 2))
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
        def to_sql(self) -> Base:
            raise NotImplementedError()
        def insert(self, session: sqlalchemy.orm.session.Session, *args, **kwargs) -> Base:
            raise NotImplementedError()
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object],
                 object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object],
                 arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations
    def ground(self) -> Action:
        return self.Action(self.object_source_description.resolve(), self.object_container_description.resolve(), self.arms[0], self.durations[0])
