class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_source, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_source} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_source, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            pour_loc = CostmapLocation(target=self.object_container, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pour_pose = next(iter(pour_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to pour the object: {self.object_container} with arm: {self.arm}")
            NavigateAction([pour_pose.pose]).resolve().perform()
            pour_pose.pose.position.z += 0.2
            pour_pose.pose.orientation = multiply_quaternions(pour_pose.pose.orientation, axis_angle_to_quaternion([0, 0, 1], math.pi/2))
            MoveTCPMotion(pour_pose.pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            pour_pose.pose.orientation = multiply_quaternions(pour_pose.pose.orientation, axis_angle_to_quaternion([0, 0, 1], -math.pi/2))
            MoveTCPMotion(pour_pose.pose, self.arm).resolve().perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations
    def ground(self) -> Action:
        source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(source_desig, container_desig, self.arms[0], self.durations[0])
