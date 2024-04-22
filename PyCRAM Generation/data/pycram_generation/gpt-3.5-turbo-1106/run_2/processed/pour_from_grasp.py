class PourAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_source_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        object_container_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arms: List[str]
        durations: List[float]
        @with_tree
        def perform(self) -> None:
            source_pose = self.object_source_desig.bullet_world_object.get_pose()
            container_pose = self.object_container_desig.bullet_world_object.get_pose()
            tilt_angle = math.pi / 2
            source_tilted_pose = source_pose.copy()
            source_tilted_pose.pose.position.z = container_pose.pose.position.z + 0.2
            source_tilted_pose.pose.orientation = multiply_quaternions(
                source_tilted_pose.pose.orientation,
                axis_angle_to_quaternion([1, 0, 0], tilt_angle)
            )
            MoveTCPMotion(source_pose, self.arms[0]).resolve().perform()
            MoveTCPMotion(container_pose, self.arms[0]).resolve().perform()
            time.sleep(self.durations[0])
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations
    def ground(self) -> Action:
        object_source_desig = self.object_source_description if (isinstance(self.object_source_description, ObjectDesignatorDescription.Object) or isinstance(self.object_source_description, ObjectPart.Object)) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if (isinstance(self.object_container_description, ObjectDesignatorDescription.Object) or isinstance(self.object_container_description, ObjectPart.Object)) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms, self.durations)
