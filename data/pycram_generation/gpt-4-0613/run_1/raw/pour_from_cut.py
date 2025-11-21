
class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)

        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_source.data_copy()
            source_object = self.object_source.bullet_world_object
            container_object = self.object_container.bullet_world_object
            source_pose = source_object.get_pose()
            container_pose = container_object.get_pose()
            container_pose.pose.position.z += 0.2
            oriR = axis_angle_to_quaternion([0, 0, 1], 90)
            container_pose.orientation.x = oriR[0]
            container_pose.orientation.y = oriR[1]
            container_pose.orientation.z = oriR[2]
            container_pose.orientation.w = oriR[3]
            MoveTCPMotion(source_pose, self.arm).resolve().perform()
            MoveTCPMotion(container_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            MoveTCPMotion(source_pose, self.arm).resolve().perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description = object_source_description
        self.object_container_description = object_container_description
        self.arms = arms
        self.durations = durations

    def ground(self) -> Action:
        object_source = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source, object_container, self.arms[0], self.durations[0])
