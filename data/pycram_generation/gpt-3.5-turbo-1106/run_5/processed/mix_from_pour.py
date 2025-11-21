class MixAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_bowl: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            bowl_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                bowl_pose = next(iter(bowl_loc))
            except StopIteration:
                raise ReachabilityFailure(f"Found no pose for the robot to reach the bowl: {self.object_bowl} with arm: {self.arm}")
            NavigateAction([bowl_pose.pose]).resolve().perform()
            MoveTCPMotion(Pose(position=bowl_pose.pose.position, orientation=[1, 0, 0, 1]), self.arm).resolve().perform()
            spiral_motions = []
            for i in range(10):
                angle = i * 2 * math.pi / 10
                spiral_motions.append(MoveTCPMotion(Pose(position=[bowl_pose.pose.position[0] + 0.1 * math.cos(angle), bowl_pose.pose.position[1] + 0.1 * math.sin(angle), bowl_pose.pose.position[2]], orientation=[1, 0, 0, 1]), self.arm))
            for motion in spiral_motions:
                motion.resolve().perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(bowl_desig, self.arms[0], self.grasps[0])
