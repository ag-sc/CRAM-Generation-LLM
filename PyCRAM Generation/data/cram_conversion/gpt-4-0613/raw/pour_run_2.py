
class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float

        @with_tree
        def perform(self) -> None:
            # Move to source object
            move_to_source = MoveTCPMotion(self.object_source.pose, self.arm).resolve()
            move_to_source.perform()

            # Pick up source object
            pick_up_source = PickUpAction(self.object_source, [self.arm], ["grasp"]).resolve()
            pick_up_source.perform()

            # Move to container object
            move_to_container = MoveTCPMotion(self.object_container.pose, self.arm).resolve()
            move_to_container.perform()

            # Pour source object into container
            tilt_pose = Pose([0, 0, 0.2], axis_angle_to_quaternion([0, 0, 1], math.pi/2), frame=self.object_container.pose.frame)
            tilt_motion = MoveTCPMotion(tilt_pose, self.arm).resolve()
            tilt_motion.perform()

            # Wait for the specified duration
            time.sleep(self.duration)

            # Return to original pose
            tilt_motion.perform(reverse=True)

            # Place source object
            place_source = PlaceAction(self.object_source, [self.object_container.pose], [self.arm]).resolve()
            place_source.perform()

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
