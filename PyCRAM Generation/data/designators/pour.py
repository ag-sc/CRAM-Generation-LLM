class PourAction(ActionDesignatorDescription):
    """
    Pours the contents of one object into another object.
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        """
        Object designator describing the object that should be poured from.
        """
        
        object_container: ObjectDesignatorDescription.Object
        """
        Object designator describing the object that should be poured into.
        """
        
        arm: str
        """
        Arm that should be used.
        """
        duration: float
        """
        Duration of the pouring.
        """
        
        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find location to pick up the source object
            pickup_loc = CostmapLocation(target=self.object_source, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pickup_pose = next(iter(pickup_loc))
            except StopIteration:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_source} with arm: {self.arm}")
            
            # navigate to source object and pick it up
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_source, self.arm, "front").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # get the dimensions of the source object
            source_dimensions = self.object_source.bullet_world_object.get_object_dimensions()
            
            # get the position of the container object
            container_position = self.object_container.pose.position
            
            # determine the gripper pose for pouring, top of source object should be 0.2 m above center of container object
            source_pose = Pose([container_position.x, container_position.y+0.5*source_dimensions[2], container_position.z+0.2], [1, 0, 0, 1])

            # find location for pouring into container object
            pour_loc = CostmapLocation(target=source_pose, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            try:
                pour_pose = next(iter(pour_loc))
            except StopIteration:
                raise ObjectUndeliverable(f"Found no pose for the robot to pour into the object: {self.object_container} with arm: {self.arm}")
                
            # navigate to container object
            NavigateAction([pour_pose.pose]).resolve().perform()
            
            # pour into container object from a height of 0.2 m above it
            MoveTCPMotion(source_pose, self.arm).resolve().perform()
            
            # perform pour for specified duration
            time.sleep(self.duration)
            
            ParkArmsAction.Action(Arms.BOTH).perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        """
        Designator describing the action of picking up a source object to be poured from,
        finding the object to be poured into and performing the pour.
        
        :param object_source_description: Object designator description or Object designator that should be poured from
        :param object_container_description: Object designator description or Object designator that should be poured into
        :param arms: List of arms to be used for action
        :param durations: List of durations for the pouring
        :param resolver: Alternative resolver returning a performable designator
        """
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        """
        Default resolver uses first entries of provided parameter lists
        
        :return: Performable designator
        """
        source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(source_desig, container_desig, self.arms[0], self.durations[0])
