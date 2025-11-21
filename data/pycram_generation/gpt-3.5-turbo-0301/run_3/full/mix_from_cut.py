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
"""
constructor:
Pose(position: Optional[List[float]] = None, orientation: Optional[List[float]] = None, frame: str = "map", time: rospy.Time = None)
"""

# object designators
from pycram.designators.object_designator import BelieveObject, ObjectPart
"""
constructors:
BelieveObject(names: Optional[List[str]] = None, types: Optional[List[str]] = None, resolver: Optional[Callable] = None) # Description for Objects that are only believed in.
ObjectPart(names: List[str], part_of: ObjectDesignatorDescription.Object, type: Optional[str] = None, resolver: Optional[Callable] = None) # Object Designator Descriptions for Objects that are part of some other object.
"""

# location designators
from pycram.designators.location_designator import CostmapLocation
"""
constructors:
CostmapLocation(target: Union[Pose, ObjectDesignatorDescription.Object], reachable_for: Optional[ObjectDesignatorDescription.Object] = None, visible_for: Optional[ObjectDesignatorDescription.Object] = None, reachable_arm: Optional[str] = None, resolver: Optional[Callable] = None) # Uses Costmaps to create locations for complex constrains
"""

# motion designators
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
"""
constructors:
MoveTCPMotion(target: Pose, arm: Optional[str] = None, resolver: Optional[Callable] = None, allow_gripper_collision: Optional[bool] = None) # Moves the Tool center point (TCP) of the robot
MoveGripperMotion(motion: str, gripper: str, resolver: Optional[Callable] = None, allow_gripper_collision: Optional[bool] = None) # Opens or closes the gripper
"""

# action designators
from pycram.designators.action_designator import MoveTorsoAction, ParkArmsAction, PickUpAction, PlaceAction, NavigateAction
"""
constructors:
MoveTorsoAction(positions: List[float], resolver=None) # Action Designator for Moving the torso of the robot up and down
ParkArmsAction(arms: List[Arms], resolver=None) # Park the arms of the robot
PickUpAction(object_designator_description:  Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None) # Designator to let the robot pick up an object
PlaceAction(object_designator_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], target_locations: List[Pose], arms: List[str], resolver=None) # Places an Object at a position using an arm
NavigateAction(target_locations: List[Pose], resolver=None) # Navigates the Robot to a position
"""


















# Pose


# object designators


# location designators


# motion designators


# action designators


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
            tool_position = np.array([0, 0, 0])
            # Get the orientation of the tool
            tool_orientation = np.array([0, 0, 0, 1])
            # Set the initial angle of the tool
            angle = 0
            # Set the radius of the spiral
            spiral_radius = bowl_radius / 2
            # Set the height of the spiral
            spiral_height = bowl_height / 2
            # Set the number of revolutions of the spiral
            num_revolutions = 2
            # Set the number of steps in the spiral
            num_steps = 20
            # Set the step size of the spiral
            step_size = 0.05
            # Set the height step size of the spiral
            height_step_size = spiral_height / num_steps
            # Set the angle step size of the spiral
            angle_step_size = 2 * math.pi / (num_steps * num_revolutions)
            # Set the height of the tool
            tool_height = bowl_height / 2
            # Set the height step size of the tool
            tool_height_step_size = height_step_size / 2
            # Set the angle step size of the tool
            tool_angle_step_size = angle_step_size / 2

            # Perform the mixing motion
            for i in range(num_revolutions * num_steps):
                # Calculate the position of the tool
                tool_position[0] = bowl_position[0] + spiral_radius * math.cos(angle)
                tool_position[1] = bowl_position[1] + spiral_radius * math.sin(angle)
                tool_position[2] = bowl_position[2] + tool_height
                # Calculate the orientation of the tool
                tool_orientation = multiply_quaternions([grasp[0], grasp[1], grasp[2], grasp[3]], [0, 0, math.sin(angle), math.cos(angle)])
                # Set the pose of the tool
                tool_pose = Pose(position=tool_position.tolist(), orientation=tool_orientation.tolist())
                # Perform the motion for moving the tool
                MoveTCPMotion(tool_pose, self.arm).resolve().perform()
                # Update the angle of the tool
                angle += angle_step_size
                # Update the height of the tool
                tool_height -= tool_height_step_size
                # Update the radius of the spiral
                spiral_radius += step_size
                # Update the height of the spiral
                spiral_height -= height_step_size
                # Update the angle step size of the tool
                tool_angle_step_size = angle_step_size / 2
                # Update the height step size of the tool
                tool_height_step_size = height_step_size / 2

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
