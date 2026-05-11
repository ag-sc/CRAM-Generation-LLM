class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        object_container_designator: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        object_source_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        object_container_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)

        @with_tree
        def perform(self) -> None:
            self.object_source_at_execution = self.object_source_designator.data_copy()
            self.object_container_at_execution = self.object_container_designator.data_copy()
            object_source = self.object_source_designator.bullet_world_object
            object_container = self.object_container_designator.bullet_world_object
            obj_dim = object_container.get_object_dimensions()
            dim = [max(obj_dim[0], obj_dim[1]), min(obj_dim[0], obj_dim[1]), obj_dim[2]]
            obj_height = dim[2]
            oTm = object_container.get_pose()
            object_container_pose = object_container.local_transformer.transform_to_object_frame(oTm, object_container)
            source_pose = object_source.get_pose()
            source_pose = object_source.local_transformer.transform_to_object_frame(source_pose, object_source)
            target_pose = object_container_pose.copy()
            target_pose.pose.position.z += obj_height + 0.2
            MoveTCPMotion(target_pose, self.arm).resolve().perform()
            pour_pose = target_pose.copy()
            pour_pose.pose.position.z -= 0.05
            oriR = axis_angle_to_quaternion([1, 0, 0], 90)
            ori = multiply_quaternions([pour_pose.orientation.x, pour_pose.orientation.y, pour_pose.orientation.z, pour_pose.orientation.w], oriR)
            pour_pose.orientation.x = ori[0]
            pour_pose.orientation.y = ori[1]
            pour_pose.orientation.z = ori[2]
            pour_pose.orientation.w = ori[3]
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            lift_pose = pour_pose.copy()
            lift_pose.pose.position.z += 0.1
            MoveTCPMotion(lift_pose, self.arm).resolve().perform()

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
