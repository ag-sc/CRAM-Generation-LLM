class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        object_container_designator: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        object_source_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        object_container_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        @with_tree
        def perform(self) -> None:
            self.object_source_at_execution = self.object_source_designator.data_copy()
            self.object_container_at_execution = self.object_container_designator.data_copy()
            source_object = self.object_source_designator.bullet_world_object
            container_object = self.object_container_designator.bullet_world_object
            source_dim = source_object.get_object_dimensions()
            container_dim = container_object.get_object_dimensions()
            sTm = source_object.get_pose()
            cTm = container_object.get_pose()
            target_pose = Pose(position=[cTm.pose.position.x, cTm.pose.position.y, cTm.pose.position.z + container_dim[2]/2 + 0.2], orientation=[0, 0, 0, 1], frame="map")
            MoveTCPMotion(sTm, self.arm).resolve().perform()
            PickUpAction(self.object_source_designator, [self.arm], ["top"], resolver=None).resolve().perform()
            PlaceAction(self.object_container_designator, [target_pose], [self.arm], resolver=None).resolve().perform()
            pour_pose = Pose(position=[cTm.pose.position.x, cTm.pose.position.y, cTm.pose.position.z + container_dim[2]/2 + 0.2], orientation=[0, 0, 1, 0], frame="map")
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
            time.sleep(self.duration)
            MoveGripperMotion("close", self.arm).resolve().perform()
            MoveTCPMotion(sTm, self.arm).resolve().perform()
            PlaceAction(self.object_source_designator, [sTm], [self.arm], resolver=None).resolve().perform()
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations
    def ground(self) -> Action:
        object_source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms[0], self.durations[0])
