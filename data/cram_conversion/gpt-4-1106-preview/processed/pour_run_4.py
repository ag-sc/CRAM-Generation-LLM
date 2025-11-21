class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]
        @with_tree
        def perform(self) -> None:
            arm = self.arms[0] if self.arms else robot_description.get_robot().get_main_arm()
            gripper = robot_description.get_robot().get_gripper(arm)
            bullet_world = BulletWorld.get_bullet_world()
            container_pose = bullet_world.get_object_position(self.object_container.name)
            pouring_pose = Pose(position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2],
                                orientation=[0, 0, 0, 1],  
                                frame=container_pose.frame)
            move_tcp_motion = MoveTCPMotion(target=pouring_pose, arm=arm)
            move_tcp_motion.resolve().perform()
            tilt_angle = 90
            tilt_duration = self.durations[0] if self.durations else 5  
            LocalTransformer.rotate_gripper(gripper, tilt_angle, tilt_duration)
            time.sleep(tilt_duration)
            LocalTransformer.rotate_gripper(gripper, -tilt_angle, tilt_duration)
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object],
                 object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object],
                 arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations
    def ground(self) -> Action:
        object_source = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source, object_container, self.arms, self.durations)
