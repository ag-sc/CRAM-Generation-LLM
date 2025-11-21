class CutAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        @with_tree
        def perform(self) -> None:
            object_pose = self.object_desig.bullet_world_object.get_pose() if isinstance(self.object_desig, ObjectDesignatorDescription.Object) else self.object_desig.part_pose
            lt = LocalTransformer()
            tool_frame = robot_description.get_tool_frame(self.arm)
            object_pose_in_tool = lt.transform_pose(object_pose, BulletWorld.robot.get_link_tf_frame(tool_frame))
            if self.technique == "halving":
                pre_cut_pose = object_pose_in_tool.copy()
                pre_cut_pose.pose.position.z -= 0.1
                MoveTCPMotion(pre_cut_pose, self.arm).resolve().perform()
                MoveGripperMotion("open", self.arm).resolve().perform()
                cut_pose = object_pose_in_tool.copy()
                cut_pose.pose.position.z -= 0.05
                MoveTCPMotion(cut_pose, self.arm).resolve().perform()
                MoveGripperMotion("close", self.arm).resolve().perform()
            elif self.technique == "slicing":
                for i in range(1, int(object_pose_in_tool.pose.position.y / self.slice_thickness)):
                    slice_pose = object_pose_in_tool.copy()
                    slice_pose.pose.position.y = i * self.slice_thickness
                    MoveTCPMotion(slice_pose, self.arm).resolve().perform()
                    MoveGripperMotion("open", self.arm).resolve().perform()
                    cut_pose = slice_pose.copy()
                    cut_pose.pose.position.z -= 0.05
                    MoveTCPMotion(cut_pose, self.arm).resolve().perform()
                    MoveGripperMotion("close", self.arm).resolve().perform()
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses
    def ground(self) -> Action:
        object_desig = self.object_description if (isinstance(self.object_description, ObjectDesignatorDescription.Object) or isinstance(self.object_description, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
