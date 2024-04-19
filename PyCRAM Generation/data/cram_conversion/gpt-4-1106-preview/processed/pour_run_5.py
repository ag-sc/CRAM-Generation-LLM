class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]
        @with_tree
        def perform(self) -> None:
            gripper_state = robot_description.get_gripper_state(self.arms[0])
            if gripper_state != "closed":
                raise Exception("Gripper is not holding an object.")
            source_pose = BulletWorld.robot.get_link_position(self.object_source.name, self.arms[0])
            container_pose = BulletWorld.robot.get_link_position(self.object_container.name)
            pouring_pose = Pose(position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2],
                                orientation=LocalTransformer.quaternion_from_euler(0, math.pi/2, 0))
            move_tcp_motion = MoveTCPMotion(target=pouring_pose, arm=self.arms[0])
            move_tcp_motion.resolve().perform()
            time.sleep(self.durations[0])
            move_tcp_motion = MoveTCPMotion(target=source_pose, arm=self.arms[0])
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
