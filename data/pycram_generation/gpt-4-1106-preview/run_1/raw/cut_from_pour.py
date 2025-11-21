
class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_target: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()

            # find location to approach the target object
            approach_loc = CostmapLocation(target=self.object_target, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                approach_pose = next(iter(approach_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to approach the object: {self.object_target} with arm: {self.arm}")

            # navigate to target object
            NavigateAction([approach_pose.pose]).resolve().perform()

            # pick up the cutting tool with the specified grasp
            PickUpAction.Action(self.object_target, self.arm, self.grasp).perform()

            # get the dimensions of the target object
            target_dimensions = self.object_target.bullet_world_object.get_object_dimensions()

            # determine the number of slices or if halving
            if self.technique == "halving":
                slice_count = 1
            elif self.technique == "slicing":
                slice_count = math.ceil(target_dimensions[1] / self.slice_thickness)
            else:
                raise ValueError(f"Unknown cutting technique: {self.technique}")

            # perform the cutting action
            for i in range(slice_count):
                # calculate the position for the current slice
                slice_offset = (i + 0.5) * self.slice_thickness if self.technique == "slicing" else 0.5 * target_dimensions[1]
                slice_pose = Pose([self.object_target.pose.position.x, self.object_target.pose.position.y + slice_offset, self.object_target.pose.position.z], [1, 0, 0, 1])

                # move the tool to the starting position of the slice
                MoveTCPMotion(slice_pose, self.arm).resolve().perform()

                # perform the slicing motion
                # Note: The actual slicing motion would require more detailed implementation based on the robot's capabilities

            # place the cutting tool back
            PlaceAction.Action(self.object_target, [approach_pose.pose], self.arm).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        target_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(target_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
