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
            approach_loc = CostmapLocation(target=self.object_target, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                approach_pose = next(iter(approach_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to approach the object: {self.object_target} with arm: {self.arm}")
            NavigateAction([approach_pose.pose]).resolve().perform()
            target_dimensions = self.object_target.bullet_world_object.get_object_dimensions()
            if self.technique == "halving":
                middle_pose = Pose([approach_pose.pose.position.x, approach_pose.pose.position.y, approach_pose.pose.position.z + target_dimensions[2] / 2], approach_pose.pose.orientation)
                MoveTCPMotion(middle_pose, self.arm).resolve().perform()
                MoveTCPMotion(Pose([middle_pose.position.x, middle_pose.position.y, middle_pose.position.z - target_dimensions[2]], middle_pose.orientation), self.arm).resolve().perform()
            elif self.technique == "slicing":
                num_slices = math.ceil(target_dimensions[1] / self.slice_thickness)
                for i in range(num_slices):
                    slice_pose = Pose([approach_pose.pose.position.x, approach_pose.pose.position.y + i * self.slice_thickness, approach_pose.pose.position.z + target_dimensions[2] / 2], approach_pose.pose.orientation)
                    MoveTCPMotion(slice_pose, self.arm).resolve().perform()
                    MoveTCPMotion(Pose([slice_pose.position.x, slice_pose.position.y, slice_pose.position.z - target_dimensions[2]], slice_pose.orientation), self.arm).resolve().perform()
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
