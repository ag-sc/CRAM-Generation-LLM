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
            pickup_pose = None
            for pose in pickup_loc:
                if self.arms[0] in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_description} with arm: {self.arms[0]}")
            pre_grasp_pose = Pose(position=[pickup_pose.pose.position[0], pickup_pose.pose.position[1], pickup_pose.pose.position[2] - 0.1])
            NavigateAction([pre_grasp_pose]).resolve().perform()
            MoveGripperMotion("open", self.arms[0]).perform()
            NavigateAction([pickup_pose.pose]).resolve().perform()
            MoveGripperMotion("close", self.arms[0]).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms
    def ground(self) -> Action:
        obj_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(obj_desig, self.arms)
