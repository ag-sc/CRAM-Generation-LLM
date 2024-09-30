
class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_description: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])

            # find location to move to pre-grasp position
            pre_grasp_loc = CostmapLocation(target=self.object_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pre_grasp_pose = next(iter(pre_grasp_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to pre-grasp the object: {self.object_description} with arm: {self.arm}")

            # adjust pre-grasp pose to be 10 cm before the object
            pre_grasp_pose.pose.position.x -= 0.1

            # navigate to pre-grasp position
            NavigateAction([pre_grasp_pose.pose]).resolve().perform()

            # open the gripper
            MoveGripperMotion("open", self.arm).resolve().perform()

            # move to the object
            MoveTCPMotion(pre_grasp_pose.pose, self.arm).resolve().perform()

            # close the gripper
            MoveGripperMotion("close", self.arm).resolve().perform()

    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms

    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, (ObjectDesignatorDescription.Object, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0])
