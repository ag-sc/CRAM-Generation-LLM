class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_to_cut: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_to_cut, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_to_cut} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_to_cut, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            cut_loc = CostmapLocation(target=self.object_to_cut, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                cut_pose = next(pose for pose in cut_loc)
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
            NavigateAction([cut_pose.pose]).resolve().perform()
            if self.technique == "halving":
                MoveTCPMotion(cut_pose).resolve().perform()
            elif self.technique == "slicing":
                object_width = self.object_to_cut.width
                num_slices = math.ceil(object_width / self.slice_thickness)
                for slice_index in range(num_slices):
                    slice_offset = slice_index * self.slice_thickness
                    slice_pose = Pose([cut_pose.position.x, cut_pose.position.y + slice_offset, cut_pose.position.z])
                    try:
                        MoveTCPMotion(slice_pose).resolve().perform()
                    except IKError:
                        raise ObjectUndeliverable(f"Found no pose for the robot to cut the object: {self.object_to_cut} with arm: {self.arm}")
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses
    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
