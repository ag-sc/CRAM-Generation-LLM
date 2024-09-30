
class TransportAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object: ObjectDesignatorDescription.Object
        target_locations: List[Pose]
        arms: List[str]
        
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            pickup_loc = CostmapLocation(target=self.object, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object} with arm: {self.arms[0]}")
            
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object, self.arms, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            for target_loc in self.target_locations:
                deliver_loc = CostmapLocation(target=target_loc, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
                try:
                    deliver_pose = next(iter(deliver_loc))
                except StopIteration:
                    raise ObjectUndeliverable(f"Found no pose for the robot to deliver the object to location: {target_loc} with arm: {self.arms[0]}")
                
                NavigateAction([deliver_pose.pose]).resolve().perform()
                PlaceAction.Action(self.object, [target_loc], self.arms).perform()
            
            ParkArmsAction.Action(Arms.BOTH).perform()
    
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], target_locations: List[Pose], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.target_locations: List[Pose] = target_locations
    
    def ground(self) -> Action:
        object_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(object_desig, self.target_locations, self.arms)
