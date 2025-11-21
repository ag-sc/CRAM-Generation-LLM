
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
            
            # find location to pick up the mixing tool
            pickup_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_bowl} with arm: {self.arm}")
            
            # navigate to mixing tool and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_bowl, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location for performing mix
            mix_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                mix_pose = next(iter(mix_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to mix the bowl: {self.object_bowl} with arm: {self.arm}")
            
            # navigate to mixing location
            NavigateAction([mix_pose.pose]).resolve().perform()
            
            # perform mixing motion
            radius_increment = 0.01
            current_radius = 0.0
            max_radius = 0.1
            angle_step = math.pi / 8
            current_angle = 0.0
            
            while current_radius < max_radius:
                x = mix_pose.pose.position.x + current_radius * math.cos(current_angle)
                y = mix_pose.pose.position.y + current_radius * math.sin(current_angle)
                z = mix_pose.pose.position.z
                
                new_pose = Pose([x, y, z])
                try:
                    MoveTCPMotion(new_pose, self.arm).resolve().perform()
                except IKError:
                    mix_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                    try:
                        mix_pose = next(iter(mix_loc))
                    except StopIteration:
                        raise ObjectUndeliverable(f"Found no pose for the robot to mix the bowl: {self.object_bowl} with arm: {self.arm}")
                    NavigateAction([mix_pose.pose]).resolve().perform()
                    MoveTCPMotion(new_pose, self.arm).resolve().perform()
                
                current_angle += angle_step
                if current_angle >= 2 * math.pi:
                    current_angle -= 2 * math.pi
                    current_radius += radius_increment
            
            ParkArmsAction.Action(Arms.BOTH).perform()
        
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    
    def ground(self) -> Action:
        bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(bowl_desig, self.arms[0], self.grasps[0])
