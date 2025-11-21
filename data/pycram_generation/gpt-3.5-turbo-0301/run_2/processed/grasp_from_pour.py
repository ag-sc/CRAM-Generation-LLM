class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_description: ObjectDesignatorDescription.Object
        arms: List[str]
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            grasp_loc = CostmapLocation(target=self.object_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                grasp_pose = next(iter(grasp_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_description} with arm: {self.arms[0]}")
            pre_grasp_pose = Pose([grasp_pose.pose.position.x - 0.1, grasp_pose.pose.position.y, grasp_pose.pose.position.z], [1, 0, 0, 1])
            pre_grasp_loc = CostmapLocation(target=pre_grasp_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                pre_grasp_pose = next(iter(pre_grasp_loc))
            except StopIteration:
                raise ReachabilityFailure(f"Found no pose for the robot to move to pre-grasp position: {pre_grasp_pose} with arm: {self.arms[0]}")
            NavigateAction([pre_grasp_pose.pose]).resolve().perform()
            MoveGripperMotion("open", self.arms[0]).resolve().perform()
            NavigateAction([grasp_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_description, self.arms[0], "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms
    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(object_desig, self.arms)
