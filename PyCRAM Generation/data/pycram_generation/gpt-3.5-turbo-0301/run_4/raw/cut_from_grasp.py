
class CutAction(ActionDesignatorDescription):
    """
    Cuts an object described by the given Object Designator description
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_desig: Union[ObjectDesignatorDescription.Object, ObjectPart.Object]
        """
        Object Designator for the object that should be cut
        """
        
        arm: str
        """
        The arm that should be used to cut
        """

        grasp: str
        """
        The grasp that should be used to hold the tool
        """

        technique: str
        """
        The technique that should be used to cut the object (halving or slicing)
        """

        slice_thickness: float
        """
        The thickness of each slice (only used for slicing technique)
        """

        @with_tree
        def perform(self) -> None:
            # get pose of object to be cut
            if isinstance(self.object_desig, ObjectPart.Object):
                object_pose = self.object_desig.part_pose
            else:
                object_pose = self.object_desig.bullet_world_object.get_pose()
            lt = LocalTransformer()
            tool_name = robot_description.get_tool_frame(self.arm)

            # calculate cut poses
            if self.technique == "halving":
                cut_poses = [object_pose.copy()]
                cut_poses[0].pose.position.z += 0.05
                cut_poses.append(object_pose.copy())
                cut_poses[1].pose.position.z -= 0.05
            elif self.technique == "slicing":
                object_width = self.object_desig.bullet_world_object.get_dimensions()[0]
                num_slices = int(object_width / self.slice_thickness)
                cut_poses = [object_pose.copy()]
                for i in range(1, num_slices):
                    new_pose = object_pose.copy()
                    new_pose.pose.position.y += i * self.slice_thickness
                    cut_poses.append(new_pose)

            # move to cut poses and perform cut
            for pose in cut_poses:
                pose_in_tool = lt.transform_pose(pose, BulletWorld.robot.get_link_tf_frame(tool_name))
                MoveTCPMotion(pose_in_tool, self.arm).resolve().perform()
                MoveGripperMotion(self.grasp, self.arm).resolve().perform()

    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], grasps: List[str], techniques: List[str], slice_thicknesses: List[float] = [0.05], resolver=None):
        """
        Will try to cut the object described by the given description. Cutting is done by performing a vertical slicing
        motion along the middle of the object (halving) or along the width of the object (slicing) using a tool in a
        specified arm with a specified grasp.

        :param object_description: Description of the object that should be cut
        :param arms: List of Arms that should be used for cutting
        :param grasps: List of Grasps that should be used to hold the tool
        :param techniques: List of Techniques that should be used to cut the object (halving or slicing)
        :param slice_thicknesses: List of slice thicknesses to use for slicing (default is 0.05)
        :param resolver: An alternative resolver to get a specified designator from the designator description
        """
        super().__init__(resolver)
        self.object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object] = object_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps
        self.techniques: List[str] = techniques
        self.slice_thicknesses: List[float] = slice_thicknesses

    def ground(self) -> Action:
        """
        Default resolver that takes the first element from the list of arms, grasps, techniques, and slice thicknesses
        and the first solution for the object designator description and returns it.

        :return: A performable action designator that contains specific arguments
        """
        object_desig = self.object_description if (isinstance(self.object_description, ObjectDesignatorDescription.Object) or isinstance(self.object_description, ObjectPart.Object)) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0], self.grasps[0], self.techniques[0], self.slice_thicknesses[0])