
class PourAction(ActionDesignatorDescription):
    """
    Pours the contents of an object into a container
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        """
        Object designator describing the source object that should be poured.
        """
        
        object_container_designator: ObjectDesignatorDescription.Object
        """
        Object designator describing the container where the contents should be poured.
        """
        
        arm: str
        """
        Arm that should be used
        """
        
        duration: float
        """
        Duration for which the object should be tilted to pour its contents
        """

        @with_tree
        def perform(self) -> None:
            robot_desig = BelieveObject(names=[robot_description.name])
            ParkArmsAction.Action(Arms.BOTH).perform()
            pickup_loc = CostmapLocation(target=self.object_source_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm)
            # Tries to find a pick-up posotion for the robot that uses the given arm
            pickup_pose = None
            for pose in pickup_loc:
                if self.arm in pose.reachable_arms:
                    pickup_pose = pose
                    break
            if not pickup_pose:
                raise ObjectUnfetchable(f"Found no pose for the robot to grasp the object: {self.object_source_designator} with arm: {self.arm}")

            # navigate to pick-up position and pick up the object
            NavigateAction([pickup_pose.pose]).resolve().perform()
            PickUpAction.Action(self.object_source_designator, self.arm, "top").perform()
            ParkArmsAction.Action(Arms.BOTH).perform()
            
            # find position for robot to stand in when placing object
            try:
                place_loc = CostmapLocation(target=self.object_container_designator, reachable_for=robot_desig.resolve(), reachable_arm=self.arm).resolve()
            except StopIteration:
                raise ReachabilityFailure(f"No location found from where the robot can reach the target location: {self.object_container_designator}")
            
            # navigate to target position and pour object
            NavigateAction([place_loc.pose]).resolve().perform()
            target_pose = Pose(position=[place_loc.pose.position.x, place_loc.pose.position.y, place_loc.pose.position.z + 0.2], orientation=axis_angle_to_quaternion([1, 0, 0, math.pi/2]))
            MoveTCPMotion(target_pose, self.arm).perform()
            time.sleep(self.duration)
            ParkArmsAction.Action(Arms.BOTH).perform()


    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        """
        Designator representing a pour plan.

        :param object_source_description: Object designator description or a specified Object designator that should be poured
        :param object_container_description: Object designator description or a specified Object designator for the container where the contents should be poured
        :param arms: A List of possible arms that could be used for transporting
        :param durations: A List of possible durations for tilting the object to pour its contents
        :param resolver: An alternative resolver that returns a performable designator for the list of possible parameter
        """
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        """
        Default resolver that returns a performable designator with the first entries from the lists of possible parameter.

        :return: A performable designator
        """
        obj_source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        obj_container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(obj_source_desig, obj_container_desig, self.arms[0], self.durations[0])
