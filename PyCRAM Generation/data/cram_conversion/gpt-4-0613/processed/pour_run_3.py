class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        @with_tree
        def perform(self) -> None:
            PickUpAction(self.object_source, [self.arm]).resolve().perform()
            container_location = CostmapLocation(self.object_container).resolve()
            MoveTCPMotion(container_location, self.arm).resolve().perform()
            tilt_pose = Pose([0, 0, 0.2], axis_angle_to_quaternion([0, 0, 1], math.pi / 2), frame=self.object_container.name)
            MoveTCPMotion(tilt_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            MoveTCPMotion(self.object_source.pose, self.arm).resolve().perform()
            PlaceAction(self.object_source, [self.object_source.pose], [self.arm]).resolve().perform()
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations
    def ground(self) -> Action:
        object_source = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source, object_container, self.arms[0], self.durations[0])
