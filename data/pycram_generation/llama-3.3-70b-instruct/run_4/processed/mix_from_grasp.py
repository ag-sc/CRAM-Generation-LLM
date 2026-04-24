class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_description: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        @with_tree
        def perform(self) -> None:
            robot = BulletWorld.robot
            object_bowl = self.object_bowl_description.bullet_world_object
            tool_frame = robot_description.get_tool_frame(self.arm)
            grasp_orientation = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            object_pose = object_bowl.get_pose()
            local_tf = LocalTransformer()
            object_pose_in_tool = local_tf.transform_pose(object_pose, robot.get_link_tf_frame(tool_frame))
            adjusted_pose = object_pose_in_tool.copy()
            adjusted_pose.pose.position.z += 0.05
            MoveTCPMotion(adjusted_pose, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()
            for _ in range(5):
                adjusted_pose.pose.position.x += 0.01
                adjusted_pose.pose.position.y += 0.01
                MoveTCPMotion(adjusted_pose, self.arm).resolve().perform()
                time.sleep(0.5)
                adjusted_pose.pose.position.x -= 0.01
                adjusted_pose.pose.position.y -= 0.01
                MoveTCPMotion(adjusted_pose, self.arm).resolve().perform()
                time.sleep(0.5)
        def to_sql(self) -> Base:
            return ORMMixAction(self.arm, self.grasp)
        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs) -> Base:
            action = super().insert(session)
            if self.object_bowl_description:
                od = self.object_bowl_description.insert(session)
                action.object = od.id
            else:
                action.object = None
            session.add(action)
            session.commit()
            return action
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description = object_bowl_description
        self.arms = arms
        self.grasps = grasps
    def ground(self) -> Action:
        obj_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0])
