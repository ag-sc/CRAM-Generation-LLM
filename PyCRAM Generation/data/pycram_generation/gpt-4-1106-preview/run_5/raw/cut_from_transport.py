
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

            # Assuming the cutting tool is already attached to the robot's arm
            # and the robot is already at the object's location

            if self.technique == "halving":
                # Perform a vertical slicing motion along the middle of the object
                # This is a simplified representation of the motion
                middle_pose = Pose(position=self.object_designator.position, orientation=axis_angle_to_quaternion([0, 1, 0], math.pi / 2))
                MoveTCPMotion(target=middle_pose, arm=self.arm).resolve().perform()
            elif self.technique == "slicing":
                # Perform vertical slicing motions along the width of the object
                # This is a simplified representation of the motions
                object_width = self.object_designator.size[0]  # Assuming the width is the size in the x dimension
                num_slices = int(object_width / self.slice_thickness)
                for i in range(num_slices):
                    slice_pose = Pose(position=[self.object_designator.position[0] + i * self.slice_thickness, self.object_designator.position[1], self.object_designator.position[2]], orientation=axis_angle_to_quaternion([0, 1, 0], math.pi / 2))
                    MoveTCPMotion(target=slice_pose, arm=self.arm).resolve().perform()

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
