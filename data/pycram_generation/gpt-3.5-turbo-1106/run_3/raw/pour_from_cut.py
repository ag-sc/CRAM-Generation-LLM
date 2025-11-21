
class PourAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float

        def perform(self) -> None:
            source_object = self.object_source.bullet_world_object
            container_object = self.object_container.bullet_world_object

            source_pose = source_object.get_pose()
            container_pose = container_object.get_pose()

            tilt_angle = math.radians(90)
            tilt_pose = Pose(
                position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2],
                orientation=[0, math.sin(tilt_angle / 2), 0, math.cos(tilt_angle / 2)]
            )

            MoveTCPMotion(source_pose, self.arm).resolve().perform()
            MoveTCPMotion(tilt_pose, self.arm).resolve().perform()
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
