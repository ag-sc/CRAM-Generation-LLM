class GraspAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object]
        arms: List[str]
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            pre_grasp_loc = CostmapLocation(target=self.object, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            pre_grasp_pose = next(iter(pre_grasp_loc))
            MoveTCPMotion(pre_grasp_pose.pose, self.arms[0]).resolve().perform()
            MoveGripperMotion("open", self.arms[0]).resolve().perform()
            grasp_loc = CostmapLocation(target=self.object, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            grasp_pose = next(iter(grasp_loc))
            NavigateAction([grasp_pose.pose]).resolve().perform()
            MoveGripperMotion("close", self.arms[0]).resolve().perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms
    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, (ObjectDesignatorDescription.Object, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(object_desig, self.arms)
