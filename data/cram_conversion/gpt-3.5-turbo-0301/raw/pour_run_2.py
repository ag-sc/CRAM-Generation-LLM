
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

class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]

        @with_tree
        def perform(self) -> None:
            world = BulletWorld()
            transformer = LocalTransformer(self.object_container.frame)
            source_desig = self.object_source.resolve()
            container_desig = self.object_container.resolve()
            source_pose = source_desig.pose
            container_pose = container_desig.pose
            source_type = source_desig.type
            container_type = container_desig.type
            source_name = source_desig.name
            container_name = container_desig.name
            source_size = source_desig.size
            container_size = container_desig.size
            source_mass = source_desig.mass
            container_mass = container_desig.mass
            source_grasps = source_desig.grasps
            container_grasps = container_desig.grasps
            source_transform = source_pose.transform
            container_transform = container_pose.transform
            source_to_container = container_transform.inverse() * source_transform
            source_to_container_position = source_to_container[:3, 3]
            source_to_container_orientation = source_to_container[:3, :3]
            source_to_container_quaternion = np.quaternion(*source_to_container_orientation)
            source_to_container_axis, source_to_container_angle = Pose.from_matrix(source_to_container).axis_angle
            source_to_container_axis_quaternion = axis_angle_to_quaternion(source_to_container_axis, source_to_container_angle)
            source_to_container_quaternion = multiply_quaternions(source_to_container_quaternion, source_to_container_axis_quaternion)
            source_to_container_pose = Pose(position=source_to_container_position, orientation=source_to_container_quaternion, frame=container_pose.frame)
            source_to_container_pose = transformer.transform(source_to_container_pose, self.object_container.frame)
            source_to_container_pose.position[2] += container_size[2] / 2 + source_size[2] / 2 + 0.2
            source_to_container_pose = transformer.transform(source_to_container_pose, "map")
            source_to_container_location = CostmapLocation(source_to_container_pose, reachable_for=self.object_source, visible_for=self.object_container, reachable_arm=self.arms[0]).resolve()
            source_to_container_motion = MoveTCPMotion(source_to_container_location.pose, arm=self.arms[0]).resolve()
            source_grasp = source_grasps[0]
            container_grasp = container_grasps[0]
            source_pickup = PickUpAction(self.object_source, self.arms, [source_grasp]).resolve()
            container_place = PlaceAction(self.object_container, [source_to_container_pose], self.arms).resolve()
            container_location = CostmapLocation(container_pose, reachable_for=self.object_container, visible_for=self.object_source, reachable_arm=self.arms[0]).resolve()
            container_motion = MoveTCPMotion(container_location.pose, arm=self.arms[0]).resolve()
            container_pickup = PickUpAction(self.object_container, self.arms, [container_grasp]).resolve()
            source_place = PlaceAction(self.object_source, [source_pose], self.arms).resolve()
            source_tilt_motion = MoveTCPMotion(source_to_container_pose, arm=self.arms[0]).resolve()
            source_tilt_motion.target.orientation = axis_angle_to_quaternion([1, 0, 0], math.pi / 2)
            source_tilt_motion.target.position[2] -= source_size[2] / 2
            source_tilt_motion.target.position[2] += container_size[2] / 2
            source_tilt_motion.target.position[2] += 0.2
            source_tilt_motion.target = transformer.transform(source_tilt_motion.target, "map")
            source_tilt_motion.target = CostmapLocation(source_tilt_motion.target, reachable_for=self.object_source, visible_for=self.object_container, reachable_arm=self.arms[0]).resolve().pose
            source_tilt_motion.target.orientation = axis_angle_to_quaternion([1, 0, 0], math.pi / 2)
            source_tilt_motion.target = transformer.transform(source_tilt_motion.target, self.object_container.frame)
            container_tilt_motion = MoveTCPMotion(container_location.pose, arm=self.arms[0]).resolve()
            container_tilt_motion.target.orientation = axis_angle_to_quaternion([1, 0, 0], math.pi / 2)
            container_tilt_motion.target.position[2] += container_size[2] / 2
            container_tilt_motion.target.position[2] += 0.2
            container_tilt_motion.target = transformer.transform(container_tilt_motion.target, "map")
            container_tilt_motion.target = CostmapLocation(container_tilt_motion.target, reachable_for=self.object_container, visible_for=self.object_source, reachable_arm=self.arms[0]).resolve().pose
            container_tilt_motion.target.orientation = axis_angle_to_quaternion([1, 0, 0], math.pi / 2)
            container_tilt_motion.target = transformer.transform(container_tilt_motion.target, self.object_container.frame)
            source_tilt_duration = self.durations[0]
            container_tilt_duration = self.durations[1]
            source_tilt_motion.duration = source_tilt_duration
            container_tilt_motion.duration = container_tilt_duration
            source_pickup.perform()
            source_to_container_motion.perform()
            container_place.perform()
            container_tilt_motion.perform()
            time.sleep(container_tilt_duration)
            container_pickup.perform()
            container_motion.perform()
            source_tilt_motion.perform()
            time.sleep(source_tilt_duration)
            source_place.perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        object_source = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source, object_container, self.arms, self.durations)
