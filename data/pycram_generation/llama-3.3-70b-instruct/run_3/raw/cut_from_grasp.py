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
            robot = BulletWorld.robot
            object = self.object_designator.bullet_world_object
            tool_frame = robot_description.get_tool_frame(self.arm)
            grasp_orientation = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            oTm = object.get_pose()
            mTo = object.local_transformer.transform_to_object_frame(oTm, object)
            adjusted_pose = self.object_designator.special_knowledge_adjustment_pose(self.grasp, mTo)
            adjusted_oTm = object.local_transformer.transform_pose(adjusted_pose, "map")
            ori = multiply_quaternions([adjusted_oTm.orientation.x, adjusted_oTm.orientation.y,
                                        adjusted_oTm.orientation.z, adjusted_oTm.orientation.w],
                                       grasp_orientation)
            adjusted_oTm.orientation.x = ori[0]
            adjusted_oTm.orientation.y = ori[1]
            adjusted_oTm.orientation.z = ori[2]
            adjusted_oTm.orientation.w = ori[3]
            if self.technique == "halving":
                cutting_pose = adjusted_oTm
            elif self.technique == "slicing":
                cutting_pose = adjusted_oTm
                cutting_pose.pose.position.x -= self.slice_thickness / 2
            MoveTCPMotion(cutting_pose, self.arm).resolve().perform()
            MoveGripperMotion("close", self.arm).resolve().perform()

        def to_sql(self) -> Base:
            return ORMCutAction(self.arm, self.grasp, self.technique, self.slice_thickness)

        def insert(self, session: sqlalchemy.orm.session.Session, *args, **kwargs) -> Base:
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action

    def __init__(self, object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        super().__init__(resolver)
        self.object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_designator_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        obj_desig = self.object_designator_description if isinstance(self.object_designator_description, ObjectDesignatorDescription.Object) else self.object_designator_description.resolve()
        return self.Action(obj_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])
