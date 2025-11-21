class WipeAction(ActionDesignatorDescription):
    """
    Wipes a rectangular area of a surface with a cloth
    """
    
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        """
        Object designator describing the object that should be used for wiping
        """
        
        location: Pose
        """
        Pose describing the center of the rectangle to be wiped
        """
        
        length: float
        """
        Rectangle length
        """
        
        width: float
        """
        Rectangle width
        """
        
        arm: str
        """
        Arm that should be used
        """
        
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location to pick up the cloth object
            pickup_loc = CostmapLocation(target=self.object_cloth, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_source} with arm: {self.arm}")
            
            # navigate to cloth object and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_cloth, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location for performing wipe
            wipe_loc = CostmapLocation(target=self.location, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                wipe_pose = next(pose for pose in wipe_loc)
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to wipe the location: {self.location} with arm: {self.arm}")
            
            # navigate to wiping location
            NavigateAction([wipe_pose.pose]).resolve().perform()
            
            # determine coordinates of corner of the rectangle to be wiped
            width_step = 0.1
            location_x = self.location.position.x - 0.5*self.length
            location_y = self.location.position.y - 0.5*self.width
            location_z = self.location.position.z
            # iterate over strips to be wiped
            for step in np.arange(0, self.width+0.5*width_step, width_step):
                # move cloth to first point in strip, reposition robor if necessary
                new_pose = Pose([location_x, location_y+step, location_z])
                try:
                    MoveTCPMotion(new_pose).resolve().perform()
                except IKError:
                    wipe_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                    try:
                        wipe_pose = next(iter(wipe_loc))
                    except StopIteration:
                        raise ObjectUndeliverable(f"Found no pose for the robot to wipe the location: {self.location} with arm: {self.arm}")
                    NavigateAction([wipe_pose.pose]).resolve().perform()
                    MoveTCPMotion(new_pose).resolve().perform()
                # move cloth to second point in strip, reposition robot if necessary
                new_pose = Pose([location_x+self.length, location_y+step, location_z])
                try:
                    MoveTCPMotion(new_pose).resolve().perform()
                except IKError:
                    wipe_loc = CostmapLocation(target=new_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
                    try:
                        wipe_pose = next(iter(wipe_loc))
                    except StopIteration:
                        raise ObjectUndeliverable(f"Found no pose for the robot to wipe the location: {self.location} with arm: {self.arm}")
                    NavigateAction([wipe_pose.pose]).resolve().perform()
                    MoveTCPMotion(new_pose).resolve().perform()
            
            ParkArmsAction.Action(Arms.BOTH).perform()
        
    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        """
        Designator describing the action of picking up a cloth object to be used for wiping,
        navigating to the surface to be wiped and wiping a rectangular part of the surface.
        
        :param object_cloth_description: Object designator description or Object designator that should be used for wiping
        :param wipe_location: List of Poses describing the centers of the rectangles to be wiped
        :param lengths: List of rectangle lengths to be used
        :param widths: List of rectangle widths to be used
        :param arms: List of arms to be used
        :param resolver: Alternative resolver returning a performable designator
        """
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms
    
    def ground(self) -> Action:
        """
        Default resolver uses first entries of provided parameter lists
        
        :return: Performable designator
        """
        cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(cloth_desig, self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
