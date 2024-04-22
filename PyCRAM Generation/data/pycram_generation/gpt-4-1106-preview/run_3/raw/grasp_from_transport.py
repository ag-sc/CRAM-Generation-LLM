
class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            pre_grasp_offset = Pose(position=[0, 0, -0.1], frame=self.object_designator.frame)
            pre_grasp_location = LocalTransformer.transform_pose(pre_grasp_offset, self.object_designator.resolve().pose)
            
            pre_grasp_loc = CostmapLocation(target=pre_grasp_location, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pre_grasp_pose = next(pre_grasp_loc, None)
            if not pre_grasp_pose:
                raise ObjectUnfetchable(f"Found no pre-grasp pose for the robot to approach the object: {self.object_designator} with arm: {self.arm}")

            NavigateAction([pre_grasp_pose.pose]).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
            
            grasp_loc = CostmapLocation(target=self.object_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            grasp_pose = next(grasp_loc, None)
            if not grasp_pose:
                raise ObjectUnfetchable(f"Found no grasp pose for the robot to grasp the object: {self.object_designator} with arm: {self.arm}")

            MoveTCPMotion(grasp_pose.pose, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_designator_description = object_designator_description
        self.arms = arms

    def ground(self) -> Action:
        obj_desig = self.object_designator_description if isinstance(self.object_designator_description, (ObjectDesignatorDescription.Object, ObjectPart.Object)) else self.object_designator_description.resolve()
        return self.Action(obj_desig, self.arms[0])
