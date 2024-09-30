class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_bowl_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the bowl: {self.object_bowl_designator} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_bowl_designator, self.arm, self.grasp).perform()
            mixing_radius = 0.05  
            mixing_depth = 0.1  
            steps = 10  
            for step in range(steps):
                angle = 2 * math.pi * step / steps
                radius = mixing_radius * (step + 1) / steps
                x_offset = radius * math.cos(angle)
                y_offset = radius * math.sin(angle)
                z_offset = -mixing_depth * (step + 1) / steps
                mixing_pose = Pose(position=[x_offset, y_offset, z_offset], orientation=[0, 0, 0, 1], frame=pickup_pose.pose.frame)
                MoveTCPMotion.Action(mixing_pose, self.arm).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        obj_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0])
