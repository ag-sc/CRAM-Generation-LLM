
class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        source_object_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        container_object_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        duration: float

        @with_tree
        def perform(self) -> None:
            source_object_pose = self.source_object_desig.bullet_world_object.get_pose() if isinstance(self.source_object_desig, ObjectDesignatorDescription.Object) else self.source_object_desig.part_pose
            container_object_pose = self.container_object_desig.bullet_world_object.get_pose() if isinstance(self.container_object_desig, ObjectDesignatorDescription.Object) else self.container_object_desig.part_pose

            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)

            source_object_pose_in_gripper = lt.transform_pose(source_object_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            container_object_pose_in_gripper = lt.transform_pose(container_object_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))

            MoveTCPMotion(source_object_pose_in_gripper, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm, allow_gripper_collision=True).resolve().perform()

            container_object_pose_in_gripper.pose.position.z += 0.2
            MoveTCPMotion(container_object_pose_in_gripper, self.arm).resolve().perform()

            tilt_angle = math.pi / 2
            tilt_axis = [0, 1, 0]
            tilt_quaternion = axis_angle_to_quaternion(tilt_axis, tilt_angle)
            tilted_pose = source_object_pose_in_gripper.copy()
            tilted_pose.pose.orientation = multiply_quaternions(source_object_pose_in_gripper.pose.orientation, tilt_quaternion)

            MoveTCPMotion(tilted_pose, self.arm).resolve().perform()

            time.sleep(self.duration)

            MoveTCPMotion(source_object_pose_in_gripper, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm, allow_gripper_collision=True).resolve().perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description = object_source_description
        self.object_container_description = object_container_description
        self.arms = arms
        self.durations = durations

    def ground(self) -> Action:
        source_object_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        container_object_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(source_object_desig, container_object_desig, self.arms[0], self.durations[0])
