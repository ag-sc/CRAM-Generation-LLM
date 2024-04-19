
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
            source_object = self.object_source_designator.bullet_world_object
            container_object = self.object_container_designator.bullet_world_object

            container_pose = container_object.get_pose()
            container_pose = container_object.local_transformer.transform_to_object_frame(container_pose, container_object)

            pour_pose = container_pose.copy()
            pour_pose.pose.position.z += 0.20

            oriR = axis_angle_to_quaternion([0, 1, 0], 90)
            ori = multiply_quaternions([pour_pose.orientation.x, pour_pose.orientation.y, pour_pose.orientation.z, pour_pose.orientation.w], oriR)
            pour_pose.orientation.x = ori[0]
            pour_pose.orientation.y = ori[1]
            pour_pose.orientation.z = ori[2]
            pour_pose.orientation.w = ori[3]

            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
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
