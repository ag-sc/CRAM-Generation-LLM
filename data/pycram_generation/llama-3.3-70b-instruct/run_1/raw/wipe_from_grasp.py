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
            PickUpAction.Action(self.object_cloth_designator, self.arm, "front").perform()
            for i in range(int(self.length // 0.1)):
                pose = self.wipe_location.copy()
                pose.pose.position.x += (i * 0.1)
                if i % 2 == 0:
                    pose.pose.position.y -= self.width / 2
                else:
                    pose.pose.position.y += self.width / 2
                MoveTCPMotion(pose, self.arm).resolve().perform()

        def to_sql(self) -> Base:
            raise NotImplementedError()

        def insert(self, session: sqlalchemy.orm.session.Session, *args, **kwargs) -> Base:
            raise NotImplementedError()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        return self.Action(self.object_cloth_description.resolve(), self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
