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
            ParkArmsAction.Action(Arms.BOTH).perform()
            if self.technique == "halving":
                middle_pose = Pose(position=[0, 0, 0.5], orientation=[0, 0, 0, 1], frame=self.object_designator.name)
                MoveTCPMotion(target=middle_pose, arm=self.arm).resolve().perform()
            elif self.technique == "slicing":
                object_width = 0.2  
                num_slices = math.ceil(object_width / self.slice_thickness)
                for i in range(num_slices):
                    slice_pose = Pose(position=[0, i * self.slice_thickness, 0.5], orientation=[0, 0, 0, 1], frame=self.object_designator.name)
                    MoveTCPMotion(target=slice_pose, arm=self.arm).resolve().perform()
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
