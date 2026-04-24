class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        arm: str
        object_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]

        def perform(self) -> Any:
            if isinstance(self.object_desig, ObjectPart.Object):
                object_pose = self.object_desig.part_pose
            else:
                object_pose = self.object_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arm)

            object_pose_in_gripper = lt.transform_pose(object_pose, 
                                                       BulletWorld.robot.get_link_tf_frame(gripper_name))

            pre_grasp = object_pose_in_gripper.copy()
            pre_grasp.pose.position.x -= 0.1

            MoveTCPMotion(pre_grasp, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()

            MoveTCPMotion(object_pose_in_gripper, self.arm, allow_gripper_collision=True).resolve().perform()
            MoveGripperMotion("close", self.arm, allow_gripper_collision=True).resolve().perform()

        def to_sql(self) -> ORMAction:
            raise NotImplementedError

        def insert(self, session: sqlalchemy.orm.session.Session, *args, **kwargs) -> ORMAction:
            raise NotImplementedError

    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms

    def ground(self) -> Action:
        return self.Action(self.arms[0], self.object_description)
