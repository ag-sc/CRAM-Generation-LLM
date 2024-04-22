class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            pre_grasp_offset = Pose(position=[0, 0, -0.1])  
            pre_grasp_location = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pre_grasp_pose = None
            for pose in pre_grasp_location:
                if self.arm in pose.reachable_arms:
                    pre_grasp_pose = pose.pose + pre_grasp_offset
                    break
            if not pre_grasp_pose:
                raise ObjectUnfetchable(f"Found no pre-grasp pose for the robot to approach the object: {self.object_designator} with arm: {self.arm}")
            NavigateAction([pre_grasp_pose]).resolve().perform()
            MoveGripperMotion.Action("open", self.arm).perform()
            grasp_pose = pre_grasp_pose - pre_grasp_offset
            MoveTCPMotion.Action(grasp_pose, self.arm).perform()
            MoveGripperMotion.Action("close", self.arm).perform()
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_designator_description = object_designator_description
        self.arms = arms
    def ground(self) -> Action:
        obj_desig = self.object_designator_description if isinstance(self.object_designator_description, (ObjectDesignatorDescription.Object, ObjectPart.Object)) else self.object_designator_description.resolve()
        return self.Action(obj_desig, self.arms[0])
