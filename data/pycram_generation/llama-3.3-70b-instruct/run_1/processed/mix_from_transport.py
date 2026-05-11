class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_description: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            bowl_loc = CostmapLocation(target=self.object_bowl_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            bowl_pose = next(iter(bowl_loc))
            NavigateAction([bowl_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_bowl_description, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            MoveTCPMotion(target=Pose(position=[bowl_pose.pose.position[0], bowl_pose.pose.position[1], bowl_pose.pose.position[2] + 0.1], orientation=[0, 0, 0, 1]), arm=self.arm).perform()
            for _ in range(5):
                MoveTCPMotion(target=Pose(position=[bowl_pose.pose.position[0] + 0.01, bowl_pose.pose.position[1] + 0.01, bowl_pose.pose.position[2] + 0.1], orientation=[0, 0, 0, 1]), arm=self.arm).perform()
                MoveTCPMotion(target=Pose(position=[bowl_pose.pose.position[0] - 0.01, bowl_pose.pose.position[1] + 0.01, bowl_pose.pose.position[2] + 0.1], orientation=[0, 0, 0, 1]), arm=self.arm).perform()
                MoveTCPMotion(target=Pose(position=[bowl_pose.pose.position[0] - 0.01, bowl_pose.pose.position[1] - 0.01, bowl_pose.pose.position[2] + 0.1], orientation=[0, 0, 0, 1]), arm=self.arm).perform()
                MoveTCPMotion(target=Pose(position=[bowl_pose.pose.position[0] + 0.01, bowl_pose.pose.position[1] - 0.01, bowl_pose.pose.position[2] + 0.1], orientation=[0, 0, 0, 1]), arm=self.arm).perform()
            PlaceAction.Action(self.object_bowl_description, self.arm, bowl_pose.pose).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description = object_bowl_description
        self.arms = arms
        self.grasps = grasps
    def ground(self) -> Action:
        obj_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0])
