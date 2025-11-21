class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]
        @with_tree
        def perform(self) -> None:
            container_pose = self.object_container.get_pose()
            pouring_pose = Pose(position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2],
                                orientation=[0, 0, 0, 1],  
                                frame=container_pose.frame)
            for arm in self.arms:
                tcp_pose = robot_description.get_tcp_pose(arm)
                tilt_angle = 90
                tilt_axis = [0, 1, 0]  
                tilt_orientation = LocalTransformer.quaternion_from_euler(0, tilt_angle, 0)
                pouring_orientation = LocalTransformer.multiply_quaternions(tcp_pose.orientation, tilt_orientation)
                pouring_pose.orientation = pouring_orientation
                move_tcp_motion = MoveTCPMotion(target=pouring_pose, arm=arm)
                move_tcp_motion.resolve().perform()
                BulletWorld.current_bullet_world.wait(self.durations[0])
                move_tcp_motion = MoveTCPMotion(target=tcp_pose, arm=arm)
                move_tcp_motion.resolve().perform()
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
