class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arm: str
        duration: float

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            pickup_loc = CostmapLocation(target=self.object_source, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_source} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_source, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            try:
                place_loc = CostmapLocation(target=self.object_container, reachable_for=robot_desig.resolve(), reachable_arm=self.arm).resolve()
            except StopIteration:
                raise ReachabilityFailure(f"No location found from where the robot can reach the target location: {self.object_container}")
            NavigateAction([place_loc.pose]).resolve().perform()
            pour_pose = place_loc.pose.copy()
            pour_pose.pose.position.z += 0.2
            BulletWorld.current_bullet_world.add_vis_axis(pour_pose)
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            pour_pose.pose.position.z -= 0.2
            BulletWorld.current_bullet_world.add_vis_axis(pour_pose)
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            start_time = time.time()
            while time.time() - start_time < self.duration:
                pour_pose.pose.position.x += 0.01
                BulletWorld.current_bullet_world.add_vis_axis(pour_pose)
                MoveTCPMotion(pour_pose, self.arm).resolve().perform()
                pour_pose.pose.position.x -= 0.01
                BulletWorld.current_bullet_world.add_vis_axis(pour_pose)
                MoveTCPMotion(pour_pose, self.arm).resolve().perform()
            PlaceAction.Action(self.object_source, self.arm, place_loc.pose).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

        def to_sql(self) -> Base:
            return ORMPourAction(self.arm, self.duration)

        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 arms: List[str], durations: List[float], resolver=None):
        super(PourAction, self).__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        return self.Action(self.object_source_description, self.object_container_description, self.arms[0], self.durations[0])
