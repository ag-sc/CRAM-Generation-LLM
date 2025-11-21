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
            container_pose = container_object.get_pose()
            source_pose = source_object.get_pose()
            pour_position = Pose(
                position=[container_pose.position.x, container_pose.position.y, container_pose.position.z + 0.2],
                orientation=container_pose.orientation,
                frame="map"
            )
            tilt_orientation = multiply_quaternions(
                [source_pose.orientation.x, source_pose.orientation.y, source_pose.orientation.z, source_pose.orientation.w],
                axis_angle_to_quaternion([1, 0, 0], 90)
            )
            pour_pose = pour_position.copy()
            pour_pose.orientation.x = tilt_orientation[0]
            pour_pose.orientation.y = tilt_orientation[1]
            pour_pose.orientation.z = tilt_orientation[2]
            pour_pose.orientation.w = tilt_orientation[3]
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            original_orientation = [source_pose.orientation.x, source_pose.orientation.y, source_pose.orientation.z, source_pose.orientation.w]
            source_pose.orientation.x = original_orientation[0]
            source_pose.orientation.y = original_orientation[1]
            source_pose.orientation.z = original_orientation[2]
            source_pose.orientation.w = original_orientation[3]
            MoveTCPMotion(source_pose, self.arm).resolve().perform()
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
