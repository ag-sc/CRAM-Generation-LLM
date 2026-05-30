class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object]
        arms: List[str]
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_description} with arm: {self.arms[0]}")
            pre_grasp_pose = Pose([pickup_pose.pose.position.x - 0.1, pickup_pose.pose.position.y, pickup_pose.pose.position.z], pickup_pose.pose.orientation)
            NavigateAction([pre_grasp_pose]).resolve().perform()
            MoveGripperMotion("open", self.arms[0]).resolve().perform()
            NavigateAction([pickup_pose.pose]).resolve().perform()
            MoveGripperMotion("close", self.arms[0]).resolve().perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms
    def ground(self) -> Action:
        return self.Action(self.object_description, self.arms)
