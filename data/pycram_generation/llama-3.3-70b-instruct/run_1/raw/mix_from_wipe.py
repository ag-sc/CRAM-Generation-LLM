class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            pickup_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_bowl} with arm: {self.arm}")
            
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_bowl, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            bowl_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                bowl_pose = next(pose for pose in bowl_loc)
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to mix the location: {self.object_bowl} with arm: {self.arm}")
            
            NavigateAction([bowl_pose.pose]).resolve().perform()
            
            radius = 0.1
            angle_step = 0.1
            for radius_step in np.arange(0, 0.5, 0.01):
                for angle in np.arange(0, 2*math.pi, angle_step):
                    new_pose = Pose([bowl_pose.pose.position.x + radius_step * math.cos(angle), 
                                    bowl_pose.pose.position.y + radius_step * math.sin(angle), 
                                    bowl_pose.pose.position.z])
                    try:
                        MoveTCPMotion(new_pose).resolve().perform()
                    except IKError:
                        bowl_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                        try:
                            bowl_pose = next(iter(bowl_loc))
                        except StopIteration:
                            raise ObjectUndeliverable(f"Found no pose for the robot to mix the location: {self.object_bowl} with arm: {self.arm}")
                        NavigateAction([bowl_pose.pose]).resolve().perform()
                        MoveTCPMotion(new_pose).resolve().perform()
                radius += 0.01
            
            ParkArmsAction.Action(Arms.BOTH).perform()
        
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    
    def ground(self) -> Action:
        bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(bowl_desig, self.arms[0], self.grasps[0])
