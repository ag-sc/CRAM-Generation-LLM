class CutAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            cut_loc = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            cut_pose = None
            for pose in cut_loc:
                if self.arm in pose.reachable_arms:
                    cut_pose = pose
                    break
            if not cut_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to cut the object: {self.object_designator} with arm: {self.arm}")
            NavigateAction([cut_pose.pose]).resolve().perform()
            MoveTCPMotion(self.calculate_cutting_poses()).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
        def calculate_cutting_poses(self) -> List[Pose]:
            pass
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
