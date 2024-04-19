
class PourAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]

        def perform(self) -> None:
            source = self.object_source.bullet_world_object
            container = self.object_container.bullet_world_object

            source_pose = source.get_pose()
            container_pose = container.get_pose()

            tilt_angle = math.radians(90)
            source_tilted_pose = source_pose.copy()
            source_tilted_pose.pose.position.z = container_pose.pose.position.z + 0.2
            source_tilted_pose.orientation = axis_angle_to_quaternion([1, 0, 0], tilt_angle)

            MoveTCPMotion(source_tilted_pose, self.arms[0]).resolve().perform()
            time.sleep(self.durations[0])

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        object_source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms, self.durations)
