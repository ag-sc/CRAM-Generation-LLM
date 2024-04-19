class PourAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        def __init__(self, object_source, object_container, arm, duration):
            self.object_source = object_source
            self.object_container = object_container
            self.arm = arm
            self.duration = duration
        @with_tree
        def perform(self):
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_source, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_source} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_source, self.arm, "top").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            container_loc = CostmapLocation(target=self.object_container, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                container_pose = next(iter(container_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to pour into the container: {self.object_container} with arm: {self.arm}")
            tilt_angle = math.pi / 2
            tilt_quaternion = axis_angle_to_quaternion([1, 0, 0], tilt_angle)
            tilt_pose = Pose([container_pose.pose.position.x, container_pose.pose.position.y, container_pose.pose.position.z + 0.2], tilt_quaternion)
            NavigateAction([tilt_pose]).resolve().perform()
            MoveTCPMotion(tilt_pose).resolve().perform()
            time.sleep(self.duration)
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_source_description, object_container_description, arms, durations, resolver=None):
        super().__init__(resolver)
        self.object_source_description = object_source_description
        self.object_container_description = object_container_description
        self.arms = arms
        self.durations = durations
    def ground(self):
        source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(source_desig, container_desig, self.arms[0], self.durations[0])
