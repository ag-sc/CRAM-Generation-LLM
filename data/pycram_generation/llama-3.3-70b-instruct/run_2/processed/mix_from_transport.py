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
            oTm = object_pose
            mTo = local_tf.transform_to_object_frame(oTm, object_bowl)
            adjusted_pose = self.object_bowl_description.special_knowledge_adjustment_pose(self.grasp, mTo)
            adjusted_oTm = local_tf.transform_pose(adjusted_pose, "map")
            ori = multiply_quaternions([adjusted_oTm.orientation.x, adjusted_oTm.orientation.y, 
                                        adjusted_oTm.orientation.z, adjusted_oTm.orientation.w], 
                                       grasp_orientation)
            adjusted_oTm.orientation.x = ori[0]
            adjusted_oTm.orientation.y = ori[1]
            adjusted_oTm.orientation.z = ori[2]
            adjusted_oTm.orientation.w = ori[3]
            prepose = local_tf.transform_pose(adjusted_oTm, tool_frame)
            prepose.pose.position.x -= 0.1
            MoveTCPMotion(prepause, self.arm).resolve().perform()
            MoveGripperMotion("open", self.arm).resolve().perform()
            MoveTCPMotion(adjusted_oTm, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()
            robot.attach(object_bowl, tool_frame)
            MoveTCPMotion(adjusted_oTm, self.arm, allow_gripper_collision=True).resolve().perform()
            for _ in range(5):
                MoveTCPMotion(Pose(position=[adjusted_oTm.position.x + 0.1, adjusted_oTm.position.y + 0.1, adjusted_oTm.position.z], 
                                        orientation=adjusted_oTm.orientation), self.arm).resolve().perform()
                time.sleep(0.5)
                MoveTCPMotion(Pose(position=[adjusted_oTm.position.x - 0.1, adjusted_oTm.position.y - 0.1, adjusted_oTm.position.z], 
                                        orientation=adjusted_oTm.orientation), self.arm).resolve().perform()
                time.sleep(0.5)
        def to_sql(self) -> Base:
            return ORMAction()
        def insert(self, session: sqlalchemy.orm.session.Session, *args, **kwargs) -> Base:
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description = object_bowl_description
        self.arms = arms
        self.grasps = grasps
    def ground(self) -> Action:
        obj_desig = self.object_bowl_description if isinstance(self.object_bowl_description, 
                                                                     ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0])
