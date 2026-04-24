class CutAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        technique: str
        slice_thickness: float
        @with_tree
        def perform(self) -> None:
            if self.technique == "halving":
                object_pose = self.object_designator.bullet_world_object.get_pose()
                lt = LocalTransformer()
                gripper_name = robot_description.get_tool_frame(self.arm)
                object_pose_in_gripper = lt.transform_pose(object_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
                cut_pose = object_pose_in_gripper.copy()
                cut_pose.pose.position.x = 0
                cut_pose.pose.position.y = 0
                cut_pose.pose.position.z = object_pose_in_gripper.pose.position.z / 2
                MoveTCPMotion(cut_pose, self.arm).resolve().perform()
                MoveGripperMotion("close", self.arm).resolve().perform()
            elif self.technique == "slicing":
                object_pose = self.object_designator.bullet_world_object.get_pose()
                lt = LocalTransformer()
                gripper_name = robot_description.get_tool_frame(self.arm)
                object_pose_in_gripper = lt.transform_pose(object_pose, BulletWorld.robot.get_link_tf_frame(gripper_name))
                cut_pose = object_pose_in_gripper.copy()
                cut_pose.pose.position.x = -self.slice_thickness / 2
                MoveTCPMotion(cut_pose, self.arm).resolve().perform()
                MoveGripperMotion("close", self.arm).resolve().perform()
                while cut_pose.pose.position.x < object_pose_in_gripper.pose.position.x + self.slice_thickness / 2:
                    cut_pose.pose.position.x += self.slice_thickness
                    MoveTCPMotion(cut_pose, self.arm).resolve().perform()
                    MoveGripperMotion("close", self.arm).resolve().perform()
        def to_sql(self) -> Base:
            raise NotImplementedError()
        def insert(self, session: sqlalchemy.orm.session.Session, *args, **kwargs) -> Base:
            raise NotImplementedError()
    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses
    def ground(self) -> Action:
        obj_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
