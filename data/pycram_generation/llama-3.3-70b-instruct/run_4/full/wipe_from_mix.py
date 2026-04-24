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
            robot = BulletWorld.robot
            cloth = self.object_cloth_designator.bullet_world_object
            wipe_surface = self.wipe_location.bullet_world_object
            cloth_dim = cloth.get_object_dimensions()
            cloth_length = cloth_dim[0]
            cloth_width = cloth_dim[1]
            cloth_height = cloth_dim[2]
            wipe_dim = wipe_surface.get_object_dimensions()
            wipe_length = wipe_dim[0]
            wipe_width = wipe_dim[1]
            wipe_height = wipe_dim[2]
            oTm = wipe_surface.get_pose()
            wipe_pose = wipe_surface.local_transformer.transform_to_object_frame(oTm, wipe_surface)
            def generate_zigzag(pose, length, width, gap, steps):
                zigzag_poses = []
                for t in range(steps):
                    tmp_pose = pose.copy()
                    x = (t % 2) * width
                    y = (t // 2) * gap
                    tmp_pose.pose.position.x += x
                    tmp_pose.pose.position.y += y
                    zigzagTm = wipe_surface.local_transformer.transform_pose(tmp_pose, "map")
                    zigzag_poses.append(zigzagTm)
                    BulletWorld.current_bullet_world.add_vis_axis(zigzagTm)
                return zigzag_poses
            zigzag_poses = generate_zigzag(wipe_pose, length, width, 0.1, int(wipe_length // 0.1))
            BulletWorld.current_bullet_world.remove_vis_axis()
            for zigzag_pose in zigzag_poses:
                oriR = axis_angle_to_quaternion([1, 0, 0], 180)
                ori = multiply_quaternions([zigzag_pose.orientation.x, zigzag_pose.orientation.y,
                                            zigzag_pose.orientation.z, zigzag_pose.orientation.w], oriR)
                adjusted_zigzag_pose = zigzag_pose.copy()
                adjusted_zigzag_pose.orientation.x = ori[0]
                adjusted_zigzag_pose.orientation.y = ori[1]
                adjusted_zigzag_pose.orientation.z = ori[2]
                adjusted_zigzag_pose.orientation.w = ori[3]
                lift_pose = adjusted_zigzag_pose.copy()
                lift_pose.pose.position.z += (wipe_height + 0.08)
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()
                MoveTCPMotion(adjusted_zigzag_pose, self.arm).resolve().perform()
                MoveTCPMotion(lift_pose, self.arm).resolve().perform()

        def to_sql(self) -> Base:
            return ORMWipeAction(self.arm)

        def insert(self, session: sqlalchemy.orm.session.Session, **kwargs):
            action = super().insert(session)
            session.add(action)
            session.commit()
            return action

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], 
                 wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super(WipeAction, self).__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        return self.Action(self.object_cloth_description.ground(), self.wipe_locations[0], self.lengths[0], self.widths[0], self.arms[0])
