class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object: ObjectDesignatorDescription.Object
        arm: str
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            grasp_loc = CostmapLocation(target=self.object, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                grasp_pose = next(iter(grasp_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object} with arm: {self.arm}")
            pre_grasp_pose = Pose([grasp_pose.pose.position.x - 0.1, grasp_pose.pose.position.y, grasp_pose.pose.position.z])
            NavigateAction([pre_grasp_pose]).resolve().perform()
            MoveGripperMotion.Action("open", self.arm).perform()
            NavigateAction([grasp_pose.pose]).resolve().perform()
            MoveGripperMotion.Action("close", self.arm).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0])
