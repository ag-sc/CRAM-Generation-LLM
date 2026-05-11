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
            cut_loc = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            cut_pose = None
            for pose in cut_loc:
                if self.arm in pose.reachable_arms:
                    cut_pose = pose
                    break
            if not cut_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to cut the object: {self.object_designator} with arm: {self.arm}")
            NavigateAction([cut_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_designator, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            if self.technique == "halving":
                MoveTCPMotion(target=Pose(position=[cut_pose.pose.position[0], cut_pose.pose.position[1], cut_pose.pose.position[2] + self.slice_thickness/2], orientation=axis_angle_to_quaternion([0, 1, 0], math.pi/2)), arm=self.arm).perform()
                MoveGripperMotion(motion="close", gripper=self.grasp, allow_gripper_collision=True).perform()
                MoveTCPMotion(target=Pose(position=[cut_pose.pose.position[0], cut_pose.pose.position[1], cut_pose.pose.position[2] - self.slice_thickness/2], orientation=axis_angle_to_quaternion([0, 1, 0], math.pi/2)), arm=self.arm).perform()
            elif self.technique == "slicing":
                for i in range(int((cut_pose.pose.position[2] - cut_pose.pose.position[2]) / self.slice_thickness)):
                    MoveTCPMotion(target=Pose(position=[cut_pose.pose.position[0], cut_pose.pose.position[1], cut_pose.pose.position[2] + i * self.slice_thickness], orientation=axis_angle_to_quaternion([0, 1, 0], math.pi/2)), arm=self.arm).perform()
                    MoveGripperMotion(motion="close", gripper=self.grasp, allow_gripper_collision=True).perform()
                    MoveTCPMotion(target=Pose(position=[cut_pose.pose.position[0], cut_pose.pose.position[1], cut_pose.pose.position[2] + (i + 1) * self.slice_thickness], orientation=axis_angle_to_quaternion([0, 1, 0], math.pi/2)), arm=self.arm).perform()
            PlaceAction.Action(self.object_designator, self.arm, cut_pose.pose).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description = object_designator_description
        self.arms = arms
        self.grasps = grasps
        self.techniques = techniques
        self.slice_thicknesses = slice_thicknesses
    def ground(self) -> Action:
        obj_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
