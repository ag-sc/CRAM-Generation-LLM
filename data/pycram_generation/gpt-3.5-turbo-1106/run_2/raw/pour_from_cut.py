
class PourAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float

        def perform(self) -> None:
            source_pose = self.object_source.get_pose()
            container_pose = self.object_container.get_pose()
            tilt_angle = 90
            source_tilted_pose = Pose(
                position=[container_pose.position.x, container_pose.position.y, container_pose.position.z + 0.2],
                orientation=axis_angle_to_quaternion([1, 0, 0], math.radians(tilt_angle)),
                frame="map"
            )
            MoveTCPMotion(source_pose, self.arm).resolve().perform()
            MoveTCPMotion(source_tilted_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            MoveTCPMotion(source_pose, self.arm).resolve().perform()

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
