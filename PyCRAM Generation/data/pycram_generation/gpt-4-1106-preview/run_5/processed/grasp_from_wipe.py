class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_description: ObjectDesignatorDescription.Object
        arm: str
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            pre_grasp_loc = CostmapLocation(target=self.object_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pre_grasp_pose = next(iter(pre_grasp_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to pre-grasp the object: {self.object_description} with arm: {self.arm}")
            pre_grasp_pose.pose.position.x -= 0.1
            NavigateAction([pre_grasp_pose.pose]).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
            grasp_pose = Pose(pre_grasp_pose.pose.position, pre_grasp_pose.pose.orientation)
            grasp_pose.position.x += 0.1
            MoveTCPMotion(grasp_pose, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, (ObjectDesignatorDescription.Object, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0])
