class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_description: ObjectDesignatorDescription.Object
        arms: str
        grasps: str
        @staticmethod
        def spiral_motion(center: Pose, radius: float, height: float, angle: float) -> Pose:
            x = center.position[0] + radius * math.cos(angle)
            y = center.position[1] + radius * math.sin(angle)
            z = center.position[2] + height
            orientation = multiply_quaternions(center.orientation, axis_angle_to_quaternion([0, 0, 1], angle))
            return Pose(position=[x, y, z], orientation=orientation)
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            bowl_loc = CostmapLocation(target=self.object_bowl_description, reachable_for=robot_desig.resolve(), reachable_arm=self.arms)
            bowl_pose = None
            for pose in bowl_loc:
                if self.arms in pose.reachable_arms:
                    bowl_pose = pose
                    break
            if not bowl_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_bowl_description} with arm: {self.arms}")
            NavigateAction([bowl_pose.pose]).resolve().perform()
            MoveTCPMotion(target=bowl_pose.pose, arm=self.arms).resolve().perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            center = bowl_pose.pose
            radius = 0.05
            height = 0.02
            angle = 0
            while angle < 2 * math.pi:
                angle += 0.1
                pose = self.spiral_motion(center, radius, height, angle)
                MoveTCPMotion(target=pose, arm=self.arms).resolve().perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description = object_bowl_description
        self.arms = arms
        self.grasps = grasps
    def ground(self) -> Action:
        obj_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0])
