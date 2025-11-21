
class GraspAction(ActionDesignatorDescription):
    
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object: ObjectDesignatorDescription.Object
        arms: List[str]
        
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location for pre-grasp position
            pre_grasp_loc = CostmapLocation(target=self.object, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                pre_grasp_pose = next(iter(pre_grasp_loc))
            except StopIteration:
                raise ReachabilityFailure(f"Found no pose for the robot to move to pre-grasp position for object: {self.object}")
            
            # move to pre-grasp position
            NavigateAction([pre_grasp_pose.pose]).resolve().perform()
            
            # open gripper
            MoveGripperMotion("open", self.arms[0]).resolve().perform()
            
            # find location for grasping object
            grasp_loc = CostmapLocation(target=self.object, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                grasp_pose = next(iter(grasp_loc))
            except StopIteration:
                raise ReachabilityFailure(f"Found no pose for the robot to grasp object: {self.object} with arm: {self.arms[0]}")
            
            # move to grasp object
            NavigateAction([grasp_pose.pose]).resolve().perform()
            
            # close gripper
            MoveGripperMotion("close", self.arms[0]).resolve().perform()
            
            ParkArmsAction.Action(Arms.BOTH).perform()
        
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms
    
    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(object_desig, self.arms)
