class MixAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            bowl_loc = CostmapLocation(target=self.object_bowl_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            bowl_pose = next(bowl_loc).pose
            NavigateAction([bowl_pose]).resolve().perform()
            MoveTCPMotion(bowl_pose, self.arm).perform()
            MoveGripperMotion("mix", self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        obj_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_bowl_desig, self.arms[0], self.grasps[0])
