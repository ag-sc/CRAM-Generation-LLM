class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        object_container_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arms: List[str]
        durations: List[float]
        @with_tree
        def perform(self) -> None:
            if isinstance(self.object_source_desig, ObjectPart.Object):
                source_pose = self.object_source_desig.part_pose
            else:
                source_pose = self.object_source_desig.bullet_world_object.get_pose()
            if isinstance(self.object_container_desig, ObjectPart.Object):
                container_pose = self.object_container_desig.part_pose
            else:
                container_pose = self.object_container_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arms[0])
            pour_pose = container_pose.copy()
            pour_pose.pose.position.z += 0.1
            pour_pose.pose.position.y += 0.1
            MoveTCPMotion(source_pose, self.arms[0]).resolve().perform()
            MoveGripperMotion("close", self.arms[0]).resolve().perform()
            MoveTCPMotion(pour_pose, self.arms[0]).resolve().perform()
            MoveTCPMotion(pour_pose, self.arms[0], allow_gripper_collision=True).resolve().perform()
            time.sleep(self.durations[0])
            MoveTCPMotion(pour_pose, self.arms[0]).resolve().perform()
            MoveGripperMotion("open", self.arms[0]).resolve().perform()
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations
    def ground(self) -> Action:
        object_source_desig = self.object_source_description if (isinstance(self.object_source_description, ObjectDesignatorDescription.Object) or isinstance(self.object_source_description, ObjectPart.Object)) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if (isinstance(self.object_container_description, ObjectDesignatorDescription.Object) or isinstance(self.object_container_description, ObjectPart.Object)) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms, self.durations[0])
