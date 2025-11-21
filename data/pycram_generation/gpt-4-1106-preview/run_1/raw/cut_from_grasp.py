
class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
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
                cutting_pose = object_pose_in_tool.copy()
                cutting_pose.pose.position.z += object_pose_in_tool.pose.size.z / 2
                MoveTCPMotion(cutting_pose, self.arm).resolve().perform()
            elif self.technique == "slicing":
                num_slices = math.ceil(object_pose_in_tool.pose.size.x / self.slice_thickness)
                for i in range(num_slices):
                    cutting_pose = object_pose_in_tool.copy()
                    cutting_pose.pose.position.x += i * self.slice_thickness
                    MoveTCPMotion(cutting_pose, self.arm).resolve().perform()

            MoveGripperMotion(self.grasp, self.arm).resolve().perform()

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_description = object_designator_description
        self.arms = arms
        self.grasps = grasps
        self.techniques = techniques
        self.slice_thicknesses = slice_thicknesses

    def ground(self) -> Action:
        object_desig = self.object_description if (isinstance(self.object_description, ObjectDesignatorDescription.Object) or isinstance(self.object_description, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
