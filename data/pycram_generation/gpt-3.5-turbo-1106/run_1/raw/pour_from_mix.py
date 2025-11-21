
class PourAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        object_source_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        object_container_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)

        @with_tree
        def perform(self) -> None:
            self.object_source_at_execution = self.object_source.data_copy()
            self.object_container_at_execution = self.object_container.data_copy()
            source_object = self.object_source.bullet_world_object
            container_object = self.object_container.bullet_world_object

            source_dim = source_object.get_object_dimensions()
            source_height = source_dim[2]
            source_pose = source_object.get_pose()

            container_pose = container_object.get_pose()
            container_center = container_pose.pose.position
            container_center.z += source_height / 2 + 0.2

            tilt_pose = Pose(container_center, [0, 0, 0, 1], "map")
            tilt_pose.pose.position.z += 0.2

            MoveTCPMotion(tilt_pose, self.arm).resolve().perform()

            time.sleep(self.duration)

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
