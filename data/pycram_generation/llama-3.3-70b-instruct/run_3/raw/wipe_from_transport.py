class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_location: Pose
        length: float
        width: float
        arm: str

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_cloth_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_cloth_designator} with arm: {self.arm}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth_designator, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            try:
                place_loc = CostmapLocation(target=self.wipe_location, reachable_for=robot_desig.resolve(), reachable_arm=self.arm).resolve()
            except StopIteration:
                raise ReachabilityFailure(f"No location found from where the robot can reach the target location: {self.wipe_location}")
            NavigateAction([place_loc.pose]).resolve().perform()
            MoveTCPMotion(Pose(position=[self.wipe_location.position.x, self.wipe_location.position.y, self.wipe_location.position.z + 0.1], 
                             orientation=self.wipe_location.orientation), self.arm).resolve().perform()
            for i in range(int(self.length // 0.1)):
                if i % 2 == 0:
                    MoveTCPMotion(Pose(position=[self.wipe_location.position.x + i * 0.1, self.wipe_location.position.y - self.width / 2, 
                                         self.wipe_location.position.z], 
                                     orientation=self.wipe_location.orientation), self.arm).resolve().perform()
                else:
                    MoveTCPMotion(Pose(position=[self.wipe_location.position.x + i * 0.1, self.wipe_location.position.y + self.width / 2, 
                                         self.wipe_location.position.z], 
                                     orientation=self.wipe_location.orientation), self.arm).resolve().perform()
            MoveTCPMotion(Pose(position=[self.wipe_location.position.x, self.wipe_location.position.y, self.wipe_location.position.z + 0.1], 
                             orientation=self.wipe_location.orientation), self.arm).resolve().perform()
            PlaceAction.Action(self.object_cloth_designator, self.arm, self.wipe_location).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()

        def to_sql(self) -> Base:
            raise NotImplementedError()

        def insert(self, session: sqlalchemy.orm.session.Session, *args, **kwargs) -> Base:
            raise NotImplementedError()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        obj_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(obj_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
