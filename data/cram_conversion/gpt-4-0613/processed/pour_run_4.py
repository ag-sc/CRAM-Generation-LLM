class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        @with_tree
        def perform(self) -> None:
            move_to_source = MoveTCPMotion(self.object_source.pose, self.arm).resolve()
            move_to_source.perform()
            grasp_source = MoveGripperMotion('close', self.arm).resolve()
            grasp_source.perform()
            move_to_container = MoveTCPMotion(self.object_container.pose, self.arm).resolve()
            move_to_container.perform()
            pour_pose = Pose(self.object_container.pose.position, axis_angle_to_quaternion([0, 0, 1], math.pi/2), frame="map")
            pour_motion = MoveTCPMotion(pour_pose, self.arm).resolve()
            pour_motion.perform()
            time.sleep(self.duration)
            upright_pose = Pose(self.object_source.pose.position, axis_angle_to_quaternion([0, 0, 1], 0), frame="map")
            upright_motion = MoveTCPMotion(upright_pose, self.arm).resolve()
            upright_motion.perform()
            release_source = MoveGripperMotion('open', self.arm).resolve()
            release_source.perform()
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations
    def ground(self) -> Action:
        object_source = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source, object_container, self.arms[0], self.durations[0])
