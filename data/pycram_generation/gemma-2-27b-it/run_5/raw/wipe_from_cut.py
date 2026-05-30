class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arm: str

        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)

        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_cloth.data_copy()
            # Perform wiping action here

        def to_sql(self) -> ORMWipeAction:
            return ORMWipeAction(self.arm)

        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action

    def __init__(self, object_cloth_description: ObjectDesignatorDescription, wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super(WipeAction, self).__init__(resolver)
        self.object_cloth_description: ObjectDesignatorDescription = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def __iter__(self):
        for object_cloth, wipe_location, length, width, arm in itertools.product(iter(self.object_cloth_description),
                                                                               self.wipe_locations,
                                                                               self.lengths,
                                                                               self.widths,
                                                                               self.arms):
            yield self.Action(object_cloth, [wipe_location], [length], [width], arm)

    def ground(self) -> Action:
        return next(iter(self))