class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_bowl_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_bowl_designator} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_bowl_designator, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            for i in range(10):
                MoveTCPMotion(target=Pose([0, 0, i * 0.01], multiply_quaternions(axis_angle_to_quaternion([0, 0, 1], math.pi / 4), pickup_pose.pose.orientation)), arm=self.arm).resolve().perform()
                time.sleep(0.1)
            for i in range(10):
                MoveTCPMotion(target=Pose([i * 0.01, 0, 0.1], multiply_quaternions(axis_angle_to_quaternion([0, 0, 1], math.pi / 4), pickup_pose.pose.orientation)), arm=self.arm).resolve().perform()
                time.sleep(0.1)
            for i in range(10):
                MoveTCPMotion(target=Pose([0.1, i * 0.01, 0.1 - i * 0.01], multiply_quaternions(axis_angle_to_quaternion([0, 0, 1], math.pi / 4), pickup_pose.pose.orientation)), arm=self.arm).resolve().perform()
                time.sleep(0.1)
            for i in range(10):
                MoveTCPMotion(target=Pose([0.1 - i * 0.01, 0.1, 0], multiply_quaternions(axis_angle_to_quaternion([0, 0, 1], math.pi / 4), pickup_pose.pose.orientation)), arm=self.arm).resolve().perform()
                time.sleep(0.1)
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        obj_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0])
