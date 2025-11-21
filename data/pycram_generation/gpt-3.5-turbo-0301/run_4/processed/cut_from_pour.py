class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_description: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_description} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_description, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            object_dimensions = self.object_description.bullet_world_object.get_object_dimensions()
            object_position = self.object_description.pose.position
            if self.technique == 'halving':
                cut_pose = Pose([object_position.x, object_position.y, object_position.z+0.5*object_dimensions[2]], [1, 0, 0, 1])
            elif self.technique == 'slicing':
                cut_pose = Pose([object_position.x, object_position.y, object_position.z+0.5*object_dimensions[2]], [1, 0, 0, 1])
            cut_loc = CostmapLocation(target=cut_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                cut_pose = next(iter(cut_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to cut/slice the object: {self.object_description} with arm: {self.arm}")
            NavigateAction([cut_pose.pose]).resolve().perform()
            if self.technique == 'halving':
                MoveTCPMotion(Pose([object_position.x, object_position.y, object_position.z+0.5*object_dimensions[2]], [1, 0, 0, 1]), self.arm).resolve().perform()
            elif self.technique == 'slicing':
                for i in range(int(object_dimensions[1]/self.slice_thickness)):
                    MoveTCPMotion(Pose([object_position.x, object_position.y+i*self.slice_thickness, object_position.z+0.5*object_dimensions[2]], [1, 0, 0, 1]), self.arm).resolve().perform()
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
