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
            bowl_loc = CostmapLocation(target=self.object_bowl_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            bowl_pose = None
            for pose in bowl_loc:
                if self.arm in pose.reachable_arms:
                    bowl_pose = pose
                    break
            if not bowl_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the bowl: {self.object_bowl_designator} with arm: {self.arm}")
            NavigateAction([bowl_pose.pose]).resolve().perform()
            MoveGripperMotion(motion="open", gripper=self.arm).resolve().perform()
            MoveTCPMotion(target=bowl_pose.pose, arm=self.arm).resolve().perform()
            MoveGripperMotion(motion="close", gripper=self.arm).resolve().perform()
            for _ in range(3):
                MoveTCPMotion(target=[bowl_pose.pose.position[0], bowl_pose.pose.position[1], bowl_pose.pose.position[2] + 0.1], arm=self.arm).resolve().perform()
                MoveTCPMotion(target=[bowl_pose.pose.position[0] + 0.1, bowl_pose.pose.position[1], bowl_pose.pose.position[2]], arm=self.arm).resolve().perform()
                MoveTCPMotion(target=[bowl_pose.pose.position[0], bowl_pose.pose.position[1] + 0.1, bowl_pose.pose.position[2]], arm=self.arm).resolve().perform()
                MoveTCPMotion(target=[bowl_pose.pose.position[0] - 0.1, bowl_pose.pose.position[1], bowl_pose.pose.position[2]], arm=self.arm).resolve().perform()
                MoveTCPMotion(target=[bowl_pose.pose.position[0], bowl_pose.pose.position[1] - 0.1, bowl_pose.pose.position[2]], arm=self.arm).resolve().perform()
            MoveGripperMotion(motion="open", gripper=self.arm).resolve().perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        obj_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0])
