
class PourAction(ActionDesignatorDescription):
    """
    Pours the contents of an object into another object
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        """
        Object Designator for the source object that should be poured
        """
        object_container_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        """
        Object Designator for the container object that should receive the pour
        """
        arms: List[str]
        """
        The arms that should be used to pour
        """
        durations: List[float]
        """
        The duration of the pour in seconds
        """

        @with_tree
        def perform(self) -> None:
            # get pose of source object
            if isinstance(self.object_source_desig, ObjectPart.Object):
                source_pose = self.object_source_desig.part_pose
            else:
                source_pose = self.object_source_desig.bullet_world_object.get_pose()

            # get pose of container object
            if isinstance(self.object_container_desig, ObjectPart.Object):
                container_pose = self.object_container_desig.part_pose
            else:
                container_pose = self.object_container_desig.bullet_world_object.get_pose()

            lt = LocalTransformer()
            gripper_name = robot_description.get_tool_frame(self.arms[0])

            # calculate pour pose
            pour_pose = container_pose.copy()
            pour_pose.pose.position.z += 0.1
            pour_pose.pose.position.y += 0.1

            # move to source object and grasp it
            MoveTCPMotion(source_pose, self.arms[0]).resolve().perform()
            MoveGripperMotion("close", self.arms[0]).resolve().perform()

            # move to pour pose and tilt source object
            MoveTCPMotion(pour_pose, self.arms[0], allow_gripper_collision=True).resolve().perform()
            MoveTCPMotion(pour_pose, self.arms[0], orientation=axis_angle_to_quaternion([1, 0, 0], math.pi/2), allow_gripper_collision=True).resolve().perform()

            # pour for specified duration
            time.sleep(self.durations[0])

            # move back to pour pose and untilt source object
            MoveTCPMotion(pour_pose, self.arms[0], orientation=axis_angle_to_quaternion([1, 0, 0], -math.pi/2), allow_gripper_collision=True).resolve().perform()

            # move to container object and release source object
            MoveTCPMotion(container_pose, self.arms[0], allow_gripper_collision=True).resolve().perform()
            MoveGripperMotion("open", self.arms[0], allow_gripper_collision=True).resolve().perform()


    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], durations: List[float], resolver=None):
        """
        Will try to pour the contents of the source object into the container object. Pouring is done by moving to the
        source object, grasping it, moving to the container object, tilting the source object at a 90° angle, its top being
        located 20 cm above the target container's center, and pouring its contents into the target container for a specified
        duration.

        :param object_source_description: Description of the source object that should be poured
        :param object_container_description: Description of the container object that should receive the pour
        :param arms: List of Arms that should be used for pouring
        :param durations: List of durations of the pour in seconds
        :param resolver: An alternative resolver to get a specified designator from the designator description
        """
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        """
        Default resolver that takes the first element from the list of arms and durations and the first solution for the
        object designator descriptions and returns it.

        :return: A performable action designator that contains specific arguments
        """
        object_source_desig = self.object_source_description if (isinstance(self.object_source_description, ObjectDesignatorDescription.Object) or isinstance(self.object_source_description, ObjectPart.Object)) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if (isinstance(self.object_container_description, ObjectDesignatorDescription.Object) or isinstance(self.object_container_description, ObjectPart.Object)) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms, self.durations[0])