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
            container_pose_in_gripper = lt.transform_pose(container_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            pouring_pose = container_pose_in_gripper.copy()
            pouring_pose.pose.position.z += 0.2
            pouring_pose.pose.orientation = multiply_quaternions(
                axis_angle_to_quaternion([1, 0, 0], math.pi / 2),
                pouring_pose.pose.orientation
            )
            MoveTCPMotion(pouring_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            MoveTCPMotion(container_pose_in_gripper, self.arm).resolve().perform()
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
