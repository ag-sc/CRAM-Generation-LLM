
class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        object_container_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        duration: float

        @with_tree
        def perform(self) -> None:
            source_pose = self.object_source_desig.bullet_world_object.get_pose()
            container_pose = self.object_container_desig.bullet_world_object.get_pose()

            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)

            # Calculate the pose for the source object above the container
            above_container_pose = container_pose.copy()
            above_container_pose.pose.position.z += 0.2

            # Transform the pose to the gripper frame
            above_container_pose_in_gripper = lt.transform_pose(above_container_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))

            # Move to the pose above the container
            MoveTCPMotion(above_container_pose_in_gripper, self.arm).resolve().perform()

            # Tilt the source object to pour
            tilt_axis = [0, 1, 0]  # Assuming y-axis is the axis to rotate around
            tilt_angle = math.pi / 2  # 90 degrees in radians
            tilt_quaternion = axis_angle_to_quaternion(tilt_axis, tilt_angle)
            current_orientation = above_container_pose_in_gripper.pose.orientation
            tilted_orientation = multiply_quaternions(current_orientation, tilt_quaternion)

            tilted_pose = above_container_pose_in_gripper.copy()
            tilted_pose.pose.orientation = tilted_orientation

            MoveTCPMotion(tilted_pose, self.arm).resolve().perform()

            # Wait for the specified duration to pour
            time.sleep(self.duration)

            # Return to the pose above the container
            MoveTCPMotion(above_container_pose_in_gripper, self.arm).resolve().perform()

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
