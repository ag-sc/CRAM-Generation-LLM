class PourAction(ActionDesignatorDescription):
    @ActionDesignatorDescription.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        object_container_designator: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        @with_tree
        def perform(self) -> None:
            source_object = self.object_source_designator
            container_object = self.object_container_designator
            arm = self.arm
            duration = self.duration
            source_location = CostmapLocation(target=source_object, reachable_for=source_object, reachable_arm=arm).resolve()
            container_location = CostmapLocation(target=container_object, reachable_for=container_object, reachable_arm=arm).resolve()
            MoveTCPMotion(target=source_location, arm=arm).resolve().perform()
            MoveGripperMotion(motion='close', gripper=arm).resolve().perform()
            MoveTCPMotion(target=container_location, arm=arm).resolve().perform()
            pouring_location = Pose(position=[container_location.position[0], container_location.position[1], container_location.position[2] + 0.2], 
                                        orientation=axis_angle_to_quaternion([0, 0, 1], pi/2), frame='map')
            MoveTCPMotion(target=pouring_location, arm=arm).resolve().perform()
            time.sleep(duration)
            MoveGripperMotion(motion='open', gripper=arm).resolve().perform()
            MoveTCPMotion(target=source_location, arm=arm).resolve().perform()
            MoveGripperMotion(motion='open', gripper=arm).resolve().perform()
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description = object_source_description
        self.object_container_description = object_container_description
        self.arms = arms
        self.durations = durations
    def ground(self) -> Action:
        object_source = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source, object_container, self.arms[0], self.durations[0])
