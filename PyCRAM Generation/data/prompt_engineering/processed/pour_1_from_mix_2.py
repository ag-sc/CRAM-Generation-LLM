class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_source.data_copy()
            object_source = self.object_source.bullet_world_object
            object_container = self.object_container.bullet_world_object
            source_pose = object_source.get_pose()
            container_pose = object_container.get_pose()
            pour_pose = source_pose.copy()
            pour_pose.pose.position.x = container_pose.pose.position.x
            pour_pose.pose.position.y = container_pose.pose.position.y
            pour_pose.pose.position.z += 0.1
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            MoveTCPMotion(source_pose, self.arm).resolve().perform()
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description = object_source_description
        self.object_container_description = object_container_description
        self.arms = arms
        self.durations = durations
    def ground(self) -> Action:
        object_source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms[0], self.durations[0])
