class CutAction(ActionDesignatorDescription):
    class Action(ActionDesignatorDescription.Action):
        object_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        def perform(self) -> None:
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)
            object_pose = self.object_desig.bullet_world_object.get_pose() if isinstance(self.object_desig, ObjectDesignatorDescription.Object) else self.object_desig.part_pose
            object_pose_in_tool = lt.transform_pose(object_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
            if self.technique == "halving":
                pass  
            elif self.technique == "slicing":
                pass  
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
