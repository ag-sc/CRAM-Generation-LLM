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
            pouring_position = Pose(position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2], orientation=container_pose.orientation)
            MoveTCPMotion.Action(target=pouring_position, arm=self.arm).perform()
            tilt_angle = math.pi / 2  
            tilt_axis = [0, 1, 0]  
            tilt_orientation = axis_angle_to_quaternion(tilt_axis, tilt_angle)
            pouring_orientation = multiply_quaternions(container_pose.orientation, tilt_orientation)
            pouring_pose = Pose(position=pouring_position.position, orientation=pouring_orientation)
            MoveTCPMotion.Action(target=pouring_pose, arm=self.arm).perform()
            time.sleep(self.duration)
            MoveTCPMotion.Action(target=container_pose, arm=self.arm).perform()
            PlaceAction.Action(self.object_source_designator, self.arm, container_pose).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations
    def ground(self) -> Action:
        obj_source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        obj_container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(obj_source_desig, obj_container_desig, self.arms[0], self.durations[0])
