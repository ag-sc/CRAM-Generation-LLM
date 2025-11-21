
class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        object_container_designator: ObjectDesignatorDescription.Object
        arm: str
        duration: float

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()

            # Get the pick-up location for the source object
            pickup_loc = CostmapLocation(target=self.object_source_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = next(pickup_loc, None)
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the source object: {self.object_source_designator} with arm: {self.arm}")

            # Navigate to pick-up position and pick up the source object
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_source_designator, self.arm, "front").perform()

            # Get the location of the target container
            container_loc = CostmapLocation(target=self.object_container_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            container_pose = next(container_loc, None)
            if not container_pose:
                raise ObjectUndeliverable(f"Found no pose for the robot to approach the container object: {self.object_container_designator} with arm: {self.arm}")

            # Navigate to the container location
            NavigateAction([container_pose.pose]).resolve().perform()

            # Calculate the pouring pose 20 cm above the container's center
            container_center_pose = container_pose.pose
            pouring_pose = Pose(
                position=[container_center_pose.position[0], container_center_pose.position[1], container_center_pose.position[2] + 0.2],
                orientation=multiply_quaternions(container_center_pose.orientation, axis_angle_to_quaternion([1, 0, 0], math.pi / 2)),
                frame=container_center_pose.frame
            )

            # Move the TCP to the pouring pose
            MoveTCPMotion.Action(pouring_pose, self.arm).perform()

            # Wait for the specified duration to pour
            time.sleep(self.duration)

            # Return the source object to its original orientation
            MoveTCPMotion.Action(container_pose.pose, self.arm).perform()

            # Place the source object back down
            PlaceAction.Action(self.object_source_designator, self.arm, container_pose.pose).perform()
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
