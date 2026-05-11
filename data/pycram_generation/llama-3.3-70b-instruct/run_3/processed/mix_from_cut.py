class MixingAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        tool: str
        spiral_radius: float
        spiral_height: float
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)
        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_designator.data_copy()
            object = self.object_designator.bullet_world_object
            oTm = object.get_pose()
            object_pose = object.local_transformer.transform_to_object_frame(oTm, object)
            grasp = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            ori = multiply_quaternions([object_pose.orientation.x, object_pose.orientation.y, object_pose.orientation.z, object_pose.orientation.w], grasp)
            adjusted_object_pose = object_pose.copy()
            adjusted_object_pose.orientation.x = ori[0]
            adjusted_object_pose.orientation.y = ori[1]
            adjusted_object_pose.orientation.z = ori[2]
            adjusted_object_pose.orientation.w = ori[3]
            lift_pose = adjusted_object_pose.copy()
            lift_pose.pose.position.z += 0.1
            BulletWorld.current_bullet_world.add_vis_axis(lift_pose)
            MoveTCPMotion(lift_pose, self.arm).resolve().perform()
            for i in range(36):
                angle = i * 10
                radius = self.spiral_radius * (i / 36)
                height = self.spiral_height * (i / 36)
                pose = adjusted_object_pose.copy()
                pose.pose.position.x = radius * math.cos(math.radians(angle))
                pose.pose.position.y = radius * math.sin(math.radians(angle))
                pose.pose.position.z = height
                BulletWorld.current_bullet_world.add_vis_axis(pose)
                MoveTCPMotion(pose, self.arm).resolve().perform()
        def to_sql(self) -> None:
            return None
        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            return None
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super(MixingAction, self).__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
    def __iter__(self):
        for object_, grasp, arm in itertools.product(iter(self.object_bowl_description), self.grasps, self.arms):
            yield self.Action(object_, arm, grasp, tool="spoon", spiral_radius=0.1, spiral_height=0.1)
    def ground(self) -> Action:
        return next(iter(self))
