class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        object_container_designator: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)

        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_source_designator.data_copy()
            source = self.object_source_designator.bullet_world_object
            container = self.object_container_designator.bullet_world_object
            source_dim = source.get_object_dimensions()
            container_dim = container.get_object_dimensions()
            source_pose = source.get_pose()
            container_pose = container.get_pose()
            source_local_transformer = source.local_transformer
            container_local_transformer = container.local_transformer

            source_pose_map = source_local_transformer.transform_to_map_frame(source_pose)
            container_pose_map = container_local_transformer.transform_to_map_frame(container_pose)

            grasp = robot_description.grasps.get_orientation_for_grasp('left')
            lift_pose = source_pose_map.copy()
            lift_pose.pose.position.z += 2 * source_dim[2]
            MoveTCPMotion(lift_pose, self.arm).resolve().perform()

            transport_pose = container_pose_map.copy()
            transport_pose.pose.position.z += 2 * container_dim[2]
            MoveTCPMotion(transport_pose, self.arm).resolve().perform()

            pour_pose = container_pose_map.copy()
            pour_pose.pose.position.z += 0.2
            ori = multiply_quaternions([pour_pose.orientation.x, pour_pose.orientation.y, pour_pose.orientation.z, pour_pose.orientation.w], grasp)
            oriR = axis_angle_to_quaternion([1, 0, 0], 90)
            oriM = multiply_quaternions([oriR[0], oriR[1], oriR[2], oriR[3]], [ori[0], ori[1], ori[2], ori[3]])
            pour_pose.orientation.x = oriM[0]
            pour_pose.orientation.y = oriM[1]
            pour_pose.orientation.z = oriM[2]
            pour_pose.orientation.w = oriM[3]
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            lift_pose = source_pose_map.copy()
            lift_pose.pose.position.z += 2 * source_dim[2]
            MoveTCPMotion(lift_pose, self.arm).resolve().perform()

        def to_sql(self) -> ORMPourAction:
            return ORMPourAction(self.arm, self.duration)

        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 arms: List[str], durations: List[float], resolver=None):
        super(PourAction, self).__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def __iter__(self):
        for object_source, object_container, arm, duration in itertools.product(iter(self.object_source_description), 
                                                                           iter(self.object_container_description), 
                                                                           self.arms, self.durations):
            yield self.Action(object_source, object_container, arm, duration)

    def ground(self) -> Action:
        return next(iter(self))
