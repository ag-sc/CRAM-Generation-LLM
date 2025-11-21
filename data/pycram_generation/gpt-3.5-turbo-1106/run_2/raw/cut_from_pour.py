
class CutAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()

            # find location to cut the object
            cut_loc = CostmapLocation(target=self.object, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                cut_pose = next(iter(cut_loc))
            except StopIteration:
                raise ReachabilityFailure(f"Found no pose for the robot to cut the object: {self.object} with arm: {self.arm}")

            # navigate to the object and cut it
            NavigateAction([cut_pose.pose]).resolve().perform()
            MoveTCPMotion(cut_pose.pose, self.arm).resolve().perform()

            if self.technique == "halving":
                # perform vertical slicing motion along the middle of the object
                pass  # perform halving technique
            elif self.technique == "slicing":
                # perform vertical slicing motions along the width of the object with specified slice thickness
                pass  # perform slicing technique

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
