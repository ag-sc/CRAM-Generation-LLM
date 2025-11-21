
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
            
            # find location to pick up the tool object
            pickup_loc = CostmapLocation(target=self.object_bowl, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_bowl} with arm: {self.arm}")
            
            # navigate to bowl object and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_bowl, self.arm, self.grasp).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # perform mixing motion
            bowl_pose = self.object_bowl.resolve().pose
            radius = 0.05
            height = 0.02
            angle_step = 0.1
            spiral_step = 0.01
            spiral_radius = 0.0
            spiral_height = 0.0
            spiral_angle = 0.0
            spiral_direction = 1
            while spiral_radius < radius:
                spiral_radius += spiral_step
                spiral_height += height
                spiral_angle += spiral_direction * angle_step
                if spiral_angle >= 2*math.pi:
                    spiral_angle -= 2*math.pi
                elif spiral_angle < 0:
                    spiral_angle += 2*math.pi
                    spiral_direction *= -1
                x = bowl_pose.position.x + spiral_radius * math.cos(spiral_angle)
                y = bowl_pose.position.y + spiral_radius * math.sin(spiral_angle)
                z = bowl_pose.position.z + spiral_height
                new_pose = Pose([x, y, z])
                try:
                    MoveTCPMotion(new_pose).resolve().perform()
                except IKError:
                    mix_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                    try:
                        mix_pose = next(iter(mix_loc))
                    except StopIteration:
                        raise ObjectUndeliverable(f"Found no pose for the robot to mix the bowl: {self.object_bowl} with arm: {self.arm}")
                    NavigateAction([mix_pose.pose]).resolve().perform()
                    MoveTCPMotion(new_pose).resolve().perform()
            
            ParkArmsAction.Action(Arms.BOTH).perform()
        
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    
    def ground(self) -> Action:
        bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(bowl_desig, self.arms[0], self.grasps[0])
