
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
            # implementation of the action
            # get the object pose
            object_pose = self.object_designator.pose
            # calculate the cutting trajectory
            cutting_trajectory = self.calculate_cutting_trajectory(object_pose, self.slice_thickness)
            # perform the cutting action
            for pose in cutting_trajectory:
                MoveTCPMotion(target=pose, arm=self.arm).resolve().perform()
                MoveGripperMotion(motion="close", gripper=self.arm).resolve().perform()
                MoveGripperMotion(motion="open", gripper=self.arm).resolve().perform()

        def calculate_cutting_trajectory(self, object_pose, slice_thickness):
            # calculate the cutting trajectory based on the object pose and slice thickness
            # this is a placeholder implementation and should be replaced with the actual calculation
            return [object_pose]

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
