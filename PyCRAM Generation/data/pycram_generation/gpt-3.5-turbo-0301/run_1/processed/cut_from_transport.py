class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_designator} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_designator, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            try:
                cut_loc = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm).resolve()
            except StopIteration:
                raise ReachabilityFailure(f"No location found from where the robot can reach the object: {self.object_designator}")
            NavigateAction([cut_loc.pose]).resolve().perform()
            if self.technique == "halving":
                MoveTCPMotion.Action(Pose(position=[0, 0, 0.1]), self.arm).perform()
                MoveTCPMotion.Action(Pose(position=[0, 0, -0.1]), self.arm).perform()
            elif self.technique == "slicing":
                for i in range(int(self.object_designator.bounding_box.dimensions[1] / self.slice_thickness)):
                    MoveTCPMotion.Action(Pose(position=[0, self.slice_thickness, 0]), self.arm).perform()
                    PlaceAction.Action(self.object_designator, self.arm, self.object_designator.pose).perform()
                    MoveTCPMotion.Action(Pose(position=[0, -self.slice_thickness, 0]), self.arm).perform()
                    PlaceAction.Action(self.object_designator, self.arm, self.object_designator.pose).perform()
            else:
                raise ValueError(f"Invalid cutting technique: {self.technique}")
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses
    def ground(self) -> Action:
        obj_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
