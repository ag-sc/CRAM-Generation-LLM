
class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        object_container_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        duration: float

        @with_tree
        def perform(self) -> None:
            # get pose of source and container objects
            source_pose = self.object_source_desig.bullet_world_object.get_pose() if isinstance(self.object_source_desig, ObjectDesignatorDescription.Object) else self.object_source_desig.part_pose
            container_pose = self.object_container_desig.bullet_world_object.get_pose() if isinstance(self.object_container_desig, ObjectDesignatorDescription.Object) else self.object_container_desig.part_pose

            # calculate the pose for pouring
            pour_pose = container_pose.copy()
            pour_pose.pose.position.z += 0.2  # 20 cm above the container's center

            # calculate the orientation for pouring (tilting 90 degrees)
            tilt_axis = [1, 0, 0]  # Assuming x-axis is the tilting axis
            tilt_angle = math.pi / 2  # 90 degrees in radians
            tilt_quaternion = axis_angle_to_quaternion(tilt_axis, tilt_angle)
            pour_pose.pose.orientation = multiply_quaternions(pour_pose.pose.orientation, tilt_quaternion)

            # move to pour pose and perform pouring action
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            time.sleep(self.duration)  # simulate pouring for the duration

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
