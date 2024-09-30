class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_cloth_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0])
            pickup_pose = None
            for pose in pickup_loc:
                if self.arms[0] in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_cloth_designator} with arm: {self.arms[0]}")
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth_designator, self.arms[0], "top").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            for i, loc in enumerate(self.wipe_locations):
                try:
                    place_loc = CostmapLocation(target=loc, reachable_for=robot_desig.resolve(), reachable_arm=self.arms[0]).resolve()
                except StopIteration:
                    raise ReachabilityFailure(f"No location found from where the robot can reach the target location: {loc}")
                NavigateAction([place_loc.pose]).resolve().perform()
                PlaceAction.Action(self.object_cloth_designator, self.arms[0], loc).perform()
                ParkArmsAction.Action(Arms.BOTH).perform()
                length = self.lengths[i]
                width = self.widths[i]
                gap = 0.1
                num_strips = math.ceil(width / gap)
                strip_width = width / num_strips
                strip_length = length
                for j in range(num_strips):
                    strip_center = Pose(position=[0, -width/2 + strip_width/2 + j*strip_width, 0], frame=place_loc.pose.frame)
                    strip_start = Pose(position=[strip_length/2, 0, 0], frame=strip_center.frame)
                    strip_end = Pose(position=[-strip_length/2, 0, 0], frame=strip_center.frame)
                    strip_poses = []
                    strip_poses.append(strip_start)
                    strip_poses.append(strip_end)
                    NavigateAction(strip_poses).resolve().perform()
                    MoveTCPMotion(strip_start, self.arms[0]).perform()
                    MoveTCPMotion(strip_end, self.arms[0]).perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    def ground(self) -> Action:
        obj_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(obj_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])
