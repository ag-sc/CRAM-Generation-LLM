class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        object_container_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        duration: float
        @with_tree
        def perform(self) -> None:
            object_source_pose = self.object_source_desig.bullet_world_object.get_pose()
            object_container_pose = self.object_container_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)
            object_source_pose_in_gripper = lt.transform_pose(object_source_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            MoveTCPMotion(object_source_pose_in_gripper, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm, allow_gripper_collision=True).resolve().perform()
            MoveTCPMotion(object_container_pose, self.arm).resolve().perform()
            pour_pose = object_container_pose.copy()
            pour_pose.pose.position.z += 0.2
            pour_orientation = axis_angle_to_quaternion([0, 1, 0], math.pi/2)
            pour_pose.pose.orientation = multiply_quaternions(pour_pose.pose.orientation, pour_orientation)
            MoveTCPMotion(pour_pose, self.arm, allow_gripper_collision=True).resolve().perform()
            time.sleep(self.duration)
            MoveTCPMotion(object_source_pose_in_gripper, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm, allow_gripper_collision=True).resolve().perform()
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description = object_source_description
        self.object_container_description = object_container_description
        self.arms = arms
        self.durations = durations
    def ground(self) -> Action:
        object_source_desig = self.object_source_description if (isinstance(self.object_source_description, ObjectDesignatorDescription.Object) or isinstance(self.object_source_description, ObjectPart.Object)) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if (isinstance(self.object_container_description, ObjectDesignatorDescription.Object) or isinstance(self.object_container_description, ObjectPart.Object)) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms[0], self.durations[0])
