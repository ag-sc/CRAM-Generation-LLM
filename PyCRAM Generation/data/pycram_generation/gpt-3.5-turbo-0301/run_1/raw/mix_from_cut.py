
import dataclasses
import time
import math
import numpy as np
from typing import List, Optional, Union

from pycram.enums import Arms
from pycram.task import with_tree
from pycram.plan_failures import ObjectUnfetchable, ReachabilityFailure, ObjectUndeliverable, IKError
from pycram.robot_descriptions import robot_description
from pycram.helper import multiply_quaternions, axis_angle_to_quaternion
from pycram.bullet_world import BulletWorld
from pycram.local_transformer import LocalTransformer
from pycram.designator import ActionDesignatorDescription
from pycram.designator import ObjectDesignatorDescription

# Pose
from pycram.pose import Pose

# object designators
from pycram.designators.object_designator import BelieveObject, ObjectPart

# location designators
from pycram.designators.location_designator import CostmapLocation

# motion designators
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion

# action designators
from pycram.designators.action_designator import MoveTorsoAction, ParkArmsAction, PickUpAction, PlaceAction, NavigateAction

class MixAction(ActionDesignatorDescription):
    """
    Designator to let the robot perform a mixing action.
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        """
        Object designator describing the bowl in which the mixing should be performed.
        """

        arm: str
        """
        The arm that should be used for mixing.
        """

        grasp: str
        """
        The grasp that should be used for mixing. For example, 'left' or 'right'.
        """

        @with_tree
        def perform(self) -> None:
            """
            Perform the mixing action using the specified bowl, arm, and grasp.
            """
            # Retrieve bowl and robot from designators
            bowl = self.object_bowl_designator.bullet_world_object
            # Get grasp orientation and target pose
            grasp = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            # Get the pose of the bowl
            bowl_pose = bowl.get_pose()
            # Get the dimensions of the bowl
            bowl_dim = bowl.get_object_dimensions()
            # Get the radius of the bowl
            bowl_radius = bowl_dim[0] / 2
            # Get the height of the bowl
            bowl_height = bowl_dim[2]
            # Get the position of the bowl
            bowl_position = np.array([bowl_pose.pose.position.x, bowl_pose.pose.position.y, bowl_pose.pose.position.z])
            # Get the orientation of the bowl
            bowl_orientation = np.array([bowl_pose.pose.orientation.x, bowl_pose.pose.orientation.y, bowl_pose.pose.orientation.z, bowl_pose.pose.orientation.w])
            # Get the position of the tool
            tool_position = np.array([bowl_position[0], bowl_position[1] + bowl_radius, bowl_position[2] + bowl_height])
            # Set the orientation of the tool
            tool_orientation = np.array([0, 0, 0, 1])
            # Set the rotation angle for the mixing motion
            rotation_angle = 0
            # Set the radius of the mixing motion
            mixing_radius = bowl_radius / 2
            # Set the height of the mixing motion
            mixing_height = bowl_height / 2
            # Set the number of revolutions for the mixing motion
            num_revolutions = 2
            # Set the number of steps for the mixing motion
            num_steps = 20
            # Set the step size for the mixing motion
            step_size = 0.05
            # Set the height step size for the mixing motion
            height_step_size = mixing_height / num_steps
            # Set the angle step size for the mixing motion
            angle_step_size = 2 * math.pi / (num_steps * num_revolutions)
            # Set the initial height for the mixing motion
            height = mixing_height
            # Set the initial angle for the mixing motion
            angle = 0
            # Perform the mixing motion
            for i in range(num_steps * num_revolutions):
                # Calculate the position of the tool for the current step
                x = mixing_radius * math.cos(angle)
                y = mixing_radius * math.sin(angle)
                z = height
                tool_position = np.array([bowl_position[0] + x, bowl_position[1] + y, bowl_position[2] + z])
                # Set the orientation of the tool for the current step
                tool_orientation = multiply_quaternions([grasp[0], grasp[1], grasp[2], grasp[3]], [0, 0, math.sin(rotation_angle / 2), math.cos(rotation_angle / 2)])
                # Set the pose of the tool for the current step
                tool_pose = Pose(position=tool_position.tolist(), orientation=tool_orientation.tolist())
                # Perform the motion for moving the tool to the current position
                MoveTCPMotion(tool_pose, self.arm).resolve().perform()
                # Update the angle for the next step
                angle += angle_step_size
                # Update the height for the next step
                height -= height_step_size
                # Update the rotation angle for the next step
                rotation_angle += 0.1
                
    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        """
        Initialize the MixAction with object designators, arms, and grasps.

        :param object_bowl_description: Object designator description or Object designator for the bowl in which the mixing should be performed.
        :param arms: List of possible arms that could be used.
        :param grasps: List of possible grasps for the mixing action.
        :param resolver: An optional resolver for dynamic parameter selection.
        """
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        """
        Default resolver, returns a performable designator with the first entries from the lists of possible parameter.

        :return: A performable designator
        """
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
