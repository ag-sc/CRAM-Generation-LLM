
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

            # Get the source object
            pickup_loc = CostmapLocation(target=self.object_source_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = next(pickup_loc, None)
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the source object: {self.object_source_designator} with arm: {self.arm}")

            # Navigate to pick-up position and pick up the source object
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_source_designator, self.arm, "front").perform()

            # Get the container object
            container_loc = CostmapLocation(target=self.object_container_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            container_pose = next(container_loc, None)
            if not container_pose:
                raise ObjectUndeliverable(f"Found no pose for the robot to approach the container object: {self.object_container_designator} with arm: {self.arm}")

            # Navigate to container position
            NavigateAction([container_pose.pose]).resolve().perform()

            # Calculate the pouring pose
            container_position = container_pose.pose.position
            pouring_position = [container_position[0], container_position[1], container_position[2] + 0.2]
            pouring_orientation = multiply_quaternions(axis_angle_to_quaternion([1, 0, 0], math.pi / 2), container_pose.pose.orientation)
            pouring_pose = Pose(position=pouring_position, orientation=pouring_orientation)

            # Move TCP to pouring position
            MoveTCPMotion.Action(pouring_pose, self.arm).perform()

            # Perform the pouring action for the specified duration
            time.sleep(self.duration)

            # Return to pick-up pose
            MoveTCPMotion.Action(pickup_pose.pose, self.arm).perform()

            # Place the source object back
            PlaceAction.Action(self.object_source_designator, self.arm, pickup_pose.pose).perform()
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
