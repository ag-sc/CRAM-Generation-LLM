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
            
            target_pose = container_pose_in_gripper.copy()
            target_pose.pose.position.z += 0.2
            
            MoveTCPMotion(target_pose, self.arm).resolve().perform()
            
            # Tilt the source object 90 degrees
            current_orientation = source_pose.orientation
            target_orientation = multiply_quaternions(current_orientation, axis_angle_to_quaternion([0, 1, 0], math.pi / 2))
            source_pose.orientation = target_orientation
            
            MoveTCPMotion(source_pose, self.arm).resolve().perform()
            
            time.sleep(self.duration)
            
            MoveTCPMotion(target_pose, self.arm).resolve().perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_source_description