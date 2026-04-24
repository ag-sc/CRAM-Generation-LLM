class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        arm: str
        @with_tree
        def perform(self) -> None:
            robot = BulletWorld.robot
            object = self.object_designator.bullet_world_object
            oTm = object.get_pose()
            mTo = object.local_transformer.transform_to_object_frame(oTm, object)
            pre_grasp_pose = mTo.copy()
            pre_grasp_pose.pose.position.x -= 0.1
            pre_grasp_pose = object.local_transformer.transform_pose(pre_grasp_pose, "map")
            MoveTCPMotion(pre_grasp_pose, self.arm).resolve().perform()
            MoveGripperMotion(motion="open", gripper=self.arm).resolve().perform()
            MoveTCPMotion(oTm, self.arm).resolve().perform()
            MoveGripperMotion(motion="close", gripper=self.arm).resolve().perform()
        def to_sql(self) -> Base:
            return ORMMoveAction(self.arm)
        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs) -> Base:
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action
    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super(GraspAction, self).__init__(resolver)
        self.object_description = object_description
        self.arms = arms
    def ground(self) -> Action:
        return self.Action(self.object_description, self.arms[0])
