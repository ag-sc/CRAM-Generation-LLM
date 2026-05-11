class TransportAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        target_location: Pose
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)

        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_designator.data_copy()
            object = self.object_designator.bullet_world_object
            PickUpAction(self.object_designator, [self.arm], [self.arm]).resolve().perform()
            MoveTCPMotion(self.target_location, self.arm).resolve().perform()
            PlaceAction(self.object_designator, [self.target_location], [self.arm]).resolve().perform()

        def to_sql(self) -> ORMTransportAction:
            return ORMTransportAction(self.arm, self.target_location)

        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], target_locations: List[Pose], resolver=None):
        super(TransportAction, self).__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.target_locations: List[Pose] = target_locations

    def __iter__(self):
        for object_, arm, target_location in itertools.product(iter(self.object_designator_description), self.arms, self.target_locations):
            yield self.Action(object_, arm, target_location)

    def ground(self) -> Action:
        return next(iter(self))
