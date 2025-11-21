class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        object_container_designator: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        @with_tree
        def perform(self) -> None:
            source_object = self.object_source_designator.bullet_world_object
            container_object = self.object_container_designator.bullet_world_object
            source_pose = source_object.get_pose()
            container_pose = container_object.get_pose()
            pour_pose = container_pose.copy()
            pour_pose.pose.position.z += 0.2  
            pour_pose.pose.orientation = multiply_quaternions(
                pour_pose.pose.orientation,
                axis_angle_to_quaternion([1, 0, 0], 90)  
            )
            MoveTCPMotion(source_pose, self.arm).resolve().perform()
            transport_pose = pour_pose.copy()
            transport_pose.pose.position.z += 0.1  
            MoveTCPMotion(transport_pose, self.arm).resolve().perform()
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            time.sleep(self.duration)  
            MoveTCPMotion(transport_pose, self.arm).resolve().perform()
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations
    def ground(self) -> Action:
        source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(source_desig, container_desig, self.arms[0], self.durations[0])
