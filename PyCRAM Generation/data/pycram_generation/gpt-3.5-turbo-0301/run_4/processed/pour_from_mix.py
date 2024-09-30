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
            PlaceAction(self.object_source_designator, [target_pose], [self.arm]).resolve().perform()
            tilt_pose = target_pose.copy()
            tilt_pose.pose.position.z += source_dim[2]/2 + 0.2
            tilt_pose.pose.orientation = axis_angle_to_quaternion([0, 1, 0], math.radians(90))
            MoveTCPMotion(tilt_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            PlaceAction(self.object_source_at_execution, [target_pose], [self.arm]).resolve().perform()
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
