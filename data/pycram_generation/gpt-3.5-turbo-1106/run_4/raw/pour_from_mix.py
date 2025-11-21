
class PourAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]

        def perform(self) -> None:
            source_object = self.object_source.bullet_world_object
            container_object = self.object_container.bullet_world_object

            source_pose = source_object.get_pose()
            container_pose = container_object.get_pose()

            tilt_angle = math.radians(90)
            tilt_pose = Pose(
                position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2],
                orientation=axis_angle_to_quaternion([1, 0, 0], tilt_angle),
                frame="map"
            )

            MoveTCPMotion(tilt_pose, self.arms[0]).resolve().perform()
            time.sleep(self.durations[0])

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(source_desig, container_desig, self.arms, self.durations)
