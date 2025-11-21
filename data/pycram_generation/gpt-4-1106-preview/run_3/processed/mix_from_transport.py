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
            bowl_loc = CostmapLocation(target=self.object_bowl_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            bowl_pose = next(bowl_loc, None)
            if not bowl_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to reach the bowl: {self.object_bowl_designator} with arm: {self.arm}")
            NavigateAction([bowl_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_bowl_designator, self.arm, self.grasp).perform()
            mixing_motion = self.generate_mixing_motion(bowl_pose.pose)
            for motion_pose in mixing_motion:
                MoveTCPMotion(motion_pose, self.arm).resolve().perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
        def generate_mixing_motion(self, bowl_pose: Pose) -> List[Pose]:
            mixing_poses = []
            radius_increment = 0.01
            angle_increment = math.pi / 16
            radius = 0.05
            angle = 0
            while radius < 0.15:
                position = [
                    bowl_pose.position[0] + radius * math.cos(angle),
                    bowl_pose.position[1] + radius * math.sin(angle),
                    bowl_pose.position[2]
                ]
                orientation = multiply_quaternions(
                    bowl_pose.orientation,
                    axis_angle_to_quaternion([0, 0, 1], -angle)
                )
                mixing_poses.append(Pose(position, orientation))
                angle += angle_increment
                if angle >= 2 * math.pi:
                    angle -= 2 * math.pi
                    radius += radius_increment
            return mixing_poses
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def ground(self) -> Action:
        obj_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_bowl_desig, self.arms[0], self.grasps[0])
