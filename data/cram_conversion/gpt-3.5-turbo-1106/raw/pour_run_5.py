
class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]

        @with_tree
        def perform(self) -> None:
            source_desig = self.object_source.resolve()
            container_desig = self.object_container.resolve()
            source_pose = Pose(position=source_desig.position, orientation=source_desig.orientation)
            container_pose = Pose(position=container_desig.position, orientation=container_desig.orientation)
            tilt_angle = math.pi / 2  # 90 degrees in radians
            tilt_quaternion = axis_angle_to_quaternion([1, 0, 0], tilt_angle)
            tilted_source_pose = Pose(position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2], orientation=multiply_quaternions(source_pose.orientation, tilt_quaternion))
            source_motion = MoveTCPMotion(target=tilted_source_pose, arm=self.arms[0])
            container_motion = MoveTCPMotion(target=container_pose, arm=self.arms[0])
            gripper_open = MoveGripperMotion(motion="open", gripper="left")
            gripper_close = MoveGripperMotion(motion="close", gripper="left")
            source_motion.resolve().perform()
            container_motion.resolve().perform()
            gripper_open.resolve().perform()
            time.sleep(self.durations[0])
            gripper_close.resolve().perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        object_source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms, self.durations)
