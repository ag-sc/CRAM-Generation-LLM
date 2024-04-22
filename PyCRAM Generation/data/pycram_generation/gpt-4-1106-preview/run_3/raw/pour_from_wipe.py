
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

            # find location to pick up the source object
            pickup_loc = CostmapLocation(target=self.object_source, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_source} with arm: {self.arm}")

            # navigate to source object and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_source, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

            # find location for performing pour
            pour_loc = CostmapLocation(target=self.object_container, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pour_pose = next(iter(pour_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to pour into the container: {self.object_container} with arm: {self.arm}")

            # navigate to pouring location
            NavigateAction([pour_pose.pose]).resolve().perform()

            # calculate the pose for pouring
            container_center = self.object_container.resolve().pose
            pour_pose = Pose([container_center.position.x, container_center.position.y, container_center.position.z + 0.2],
                             multiply_quaternions(container_center.orientation, axis_angle_to_quaternion([1, 0, 0], math.pi / 2)))

            # move source object above the container
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()

            # perform the pouring action for the specified duration
            time.sleep(self.duration)

            # return source object to upright position and place it down
            upright_pose = Pose([container_center.position.x, container_center.position.y, container_center.position.z + 0.2], container_center.orientation)
            MoveTCPMotion(upright_pose, self.arm).resolve().perform()
            PlaceAction.Action(self.object_source, [upright_pose], self.arm).perform()
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
