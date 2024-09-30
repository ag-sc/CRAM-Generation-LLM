@dataclasses.dataclass
class MixAction(ActionDesignatorDescription.Action):
    object_bowl_description: ObjectDesignatorDescription.Object
    arms: List[str]
    grasps: List[str]
    @staticmethod
    def spiral_motion(center: Pose, radius: float, height: float, angle: float, steps: int) -> List[Pose]:
        poses = []
        for i in range(steps):
            x = center.position[0] + radius * math.cos(angle * i)
            y = center.position[1] + radius * math.sin(angle * i)
            z = center.position[2] + height * i / steps
            orientation = center.orientation
            poses.append(Pose(position=[x, y, z], orientation=orientation))
        return poses
    @with_tree
    def perform(self) -> None:
        robot_desig = BelieveObject(names=[robot_description.name])
        ParkArmsAction.Action(Arms.BOTH).perform()
        bowl_loc = NavigateAction([self.object_bowl_description]).resolve()
        NavigateAction([bowl_loc.pose]).resolve().perform()
        MoveTCPMotion(target=Pose(position=[0.0, 0.0, 0.1], frame="gripper_tool_frame"), arm=self.arms[0]).resolve().perform()
        poses = self.spiral_motion(bowl_loc.pose, 0.05, 0.02, 2 * math.pi, 20)
        for pose in poses:
            NavigateAction([pose]).resolve().perform()
        MoveTCPMotion(target=Pose(position=[0.0, 0.0, 0.1], frame="gripper_tool_frame"), arm=self.arms[0]).resolve().perform()
        ParkArmsAction.Action(Arms.BOTH).perform()
class MixAction(ActionDesignatorDescription):
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description = object_bowl_description
        self.arms = arms
        self.grasps = grasps
    def ground(self) -> MixAction:
        obj_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return MixAction(obj_desig, self.arms, self.grasps)
