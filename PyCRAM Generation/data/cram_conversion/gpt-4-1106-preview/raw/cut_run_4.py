
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
            # Assuming the robot is already in front of the object and the tool is in the gripper
            # The following steps are a simplified representation of the cutting process

            # Approach object
            approach_pose = Pose([0, 0, 0.1], [0, 0, 0, 1], frame=self.object_designator.name)
            approach_motion = MoveTCPMotion(approach_pose, arm=self.arm)
            approach_motion.resolve().perform()

            # Perform cut based on technique
            if self.technique == "halving":
                # Perform a vertical slicing motion along the middle of the object
                cutting_pose = Pose([0, 0, 0], [0, 0, 0, 1], frame=self.object_designator.name)
                cutting_motion = MoveTCPMotion(cutting_pose, arm=self.arm)
                cutting_motion.resolve().perform()
            elif self.technique == "slicing":
                # Perform vertical slicing motions along the width of the object
                object_width = 0.1  # Placeholder for actual object width
                num_slices = int(object_width / self.slice_thickness)
                for i in range(num_slices):
                    cutting_pose = Pose([i * self.slice_thickness, 0, 0], [0, 0, 0, 1], frame=self.object_designator.name)
                    cutting_motion = MoveTCPMotion(cutting_pose, arm=self.arm)
                    cutting_motion.resolve().perform()

            # Retract from object
            retract_pose = Pose([0, 0, -0.1], [0, 0, 0, 1], frame=self.object_designator.name)
            retract_motion = MoveTCPMotion(retract_pose, arm=self.arm)
            retract_motion.resolve().perform()

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
