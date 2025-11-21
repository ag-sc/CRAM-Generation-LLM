class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        object_container_designator: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        object_source_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        object_container_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        @with_tree
        def perform(self) -> None:
            self.object_source_at_execution = self.object_source_designator.data_copy()
            self.object_container_at_execution = self.object_container_designator.data_copy()
            source_object = self.object_source_designator.bullet_world_object
            container_object = self.object_container_designator.bullet_world_object
            container_pose = container_object.get_pose()
            container_pose.pose.position.z += 0.2
            source_pose = source_object.get_pose()
            source_pose.pose.position.x = container_pose.pose.position.x
            source_pose.pose.position.y = container_pose.pose.position.y
            source_pose.pose.position.z = container_pose.pose.position.z + 0.2
            oriR = axis_angle_to_quaternion([1, 0, 0], 90)
            source_ori = [source_pose.orientation.x, source_pose.orientation.y, source_pose.orientation.z, source_pose.orientation.w]
            oriM = multiply_quaternions([oriR[0], oriR[1], oriR[2], oriR[3]], source_ori)
            pour_pose = source_pose.copy()
            pour_pose.orientation.x = oriM[0]
            pour_pose.orientation.y = oriM[1]
            pour_pose.orientation.z = oriM[2]
            pour_pose.orientation.w = oriM[3]
            BulletWorld.current_bullet_world.add_vis_axis(pour_pose)
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            reset_pose = source_pose.copy()
            BulletWorld.current_bullet_world.add_vis_axis(reset_pose)
            MoveTCPMotion(reset_pose, self.arm).resolve().perform()
            BulletWorld.current_bullet_world.remove_vis_axis()
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
