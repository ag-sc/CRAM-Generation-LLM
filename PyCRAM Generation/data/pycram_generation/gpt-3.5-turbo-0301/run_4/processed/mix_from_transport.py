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
            ParkArmsAction.Action(Arms.BOTH).perform()
            bowl_loc = self.object_bowl_description.resolve()
            navigate_to_bowl = NavigateAction([bowl_loc]).resolve()
            navigate_to_bowl.perform()
            move_tcp = MoveTCPMotion(target=bowl_loc, arm=self.arms, allow_gripper_collision=True).resolve()
            move_tcp.perform()
            center = bowl_loc.pose
            radius = 0.05
            height = 0.02
            angle = 0
            for i in range(10):
                angle += 2 * math.pi / 10
                pose = self.spiral_motion(center, radius, height, angle)
                move_tcp = MoveTCPMotion(target=pose, arm=self.arms, allow_gripper_collision=True).resolve()
                move_tcp.perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description = object_bowl_description
        self.arms = arms
        self.grasps = grasps
    def ground(self) -> Action:
        obj_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0])
