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
            tool_desig = ObjectPart(names=["cutting_tool"], part_of=robot_desig.resolve())
            tool_pickup_loc = CostmapLocation(target=tool_desig, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            tool_pickup_pose = next(tool_pickup_loc, None)
            if not tool_pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the tool: {tool_desig} with arm: {self.arm}")
            NavigateAction([tool_pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(tool_desig, self.arm, self.grasp).perform()
            object_loc = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            object_pose = next(object_loc, None)
            if not object_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to perform cutting on the object: {self.object_designator} with arm: {self.arm}")
            NavigateAction([object_pose.pose]).resolve().perform()
            if self.technique == "halving":
                print("Performing halving technique.")
            elif self.technique == "slicing":
                print(f"Performing slicing technique with slice thickness {self.slice_thickness}.")
            else:
                raise ValueError(f"Unknown cutting technique: {self.technique}")
            PlaceAction.Action(tool_desig, self.arm, tool_pickup_pose.pose).perform()
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
