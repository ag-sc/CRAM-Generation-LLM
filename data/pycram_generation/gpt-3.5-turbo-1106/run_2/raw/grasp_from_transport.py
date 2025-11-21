
class GraspAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object]
        arm: str

        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            pre_grasp_loc = CostmapLocation(target=self.object_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pre_grasp_pose = next(pre_grasp_loc).pose
            pre_grasp_pose.position = [pre_grasp_pose.position[0] - 0.1, pre_grasp_pose.position[1], pre_grasp_pose.position[2]]
            NavigateAction([pre_grasp_pose]).resolve().perform()
            MoveGripperMotion("open", self.arm).perform()
            NavigateAction([pre_grasp_pose]).resolve().perform()
            PickUpAction.Action(self.object_description, self.arm, "front").perform()

    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms

    def ground(self) -> Action:
        obj_desig = self.object_description if isinstance(self.object_description, (ObjectDesignatorDescription.Object, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(obj_desig, self.arms[0])
