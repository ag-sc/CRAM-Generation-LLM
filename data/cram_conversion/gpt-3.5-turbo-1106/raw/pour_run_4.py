
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
            tilted_source_pose = Pose(position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2], orientation=tilt_quaternion)
            move_source = MoveTCPMotion(target=source_pose, arm=self.arms[0])
            move_container = MoveTCPMotion(target=container_pose, arm=self.arms[0])
            tilt_source = MoveTCPMotion(target=tilted_source_pose, arm=self.arms[0])
            pour_duration = self.durations[0]
            open_gripper = MoveGripperMotion(motion="open", gripper="left")
            close_gripper = MoveGripperMotion(motion="close", gripper="left")
            move_source.resolve().perform()
            move_container.resolve().perform()
            tilt_source.resolve().perform()
            time.sleep(pour_duration)
            tilt_source.resolve().perform()
            open_gripper.resolve().perform()
            time.sleep(1)  # Assuming 1 second for pouring
            close_gripper.resolve().perform()

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
