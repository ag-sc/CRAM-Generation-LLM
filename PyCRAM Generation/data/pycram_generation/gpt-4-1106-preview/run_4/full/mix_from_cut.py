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


class MixAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_bowl_designator: ObjectDesignatorDescription.Object
        arm: str
        grasp: str
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)

        def perform(self) -> None:
            self.object_at_execution = self.object_bowl_designator.data_copy()
            grasp_orientation = robot_description.grasps.get_orientation_for_grasp(self.grasp)
            bowl = self.object_bowl_designator.bullet_world_object
            bowl_dim = bowl.get_object_dimensions()
            bowl_pose = bowl.local_transformer.transform_to_object_frame(bowl.get_pose(), bowl)

            radius = min(bowl_dim[0], bowl_dim[1]) / 2
            num_spirals = 3
            num_points_per_spiral = 10
            height_offset = bowl_dim[2] / 2

            for spiral in range(num_spirals):
                for point in range(num_points_per_spiral):
                    angle = (2 * math.pi / num_points_per_spiral) * point
                    r = radius * ((spiral * num_points_per_spiral + point) / (num_spirals * num_points_per_spiral))
                    x = r * math.cos(angle)
                    y = r * math.sin(angle)

                    mix_pose = bowl_pose.copy()
                    mix_pose.pose.position.x += x
                    mix_pose.pose.position.y += y
                    mix_pose.pose.position.z += height_offset

                    mix_pose.orientation = multiply_quaternions(
                        [mix_pose.orientation.x, mix_pose.orientation.y, mix_pose.orientation.z, mix_pose.orientation.w],
                        grasp_orientation
                    )

                    BulletWorld.current_bullet_world.add_vis_axis(mix_pose)
                    MoveTCPMotion(mix_pose, self.arm).resolve().perform()
                    BulletWorld.current_bullet_world.remove_vis_axis()

    def __init__(self, object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], grasps: List[str], resolver=None):
        super().__init__(resolver)
        self.object_bowl_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_bowl_description
        self.arms: List[str] = arms
        self.grasps: List[str] = grasps

    def ground(self) -> Action:
        object_bowl_desig = self.object_bowl_description if isinstance(self.object_bowl_description, ObjectDesignatorDescription.Object) else self.object_bowl_description.resolve()
        return self.Action(object_bowl_desig, self.arms[0], self.grasps[0])
