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
            container_loc = CostmapLocation(target=self.object_container_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm).resolve()
            NavigateAction([container_loc.pose]).resolve().perform()
            PickUpAction.Action(self.object_source_designator, self.arm, "front").perform()
            container_pose = self.object_container_designator.resolve().pose
            tilt_position = [container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2]
            tilt_orientation = multiply_quaternions(container_pose.orientation, axis_angle_to_quaternion([1, 0, 0], math.pi / 2))
            tilt_pose = Pose(position=tilt_position, orientation=tilt_orientation)
            MoveTCPMotion.Action(tilt_pose, self.arm).resolve().perform()
            time.sleep(self.duration)
            ParkArmsAction.Action(Arms.BOTH).perform()
            PlaceAction.Action(self.object_source_designator, self.arm, container_loc.pose).perform()
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
