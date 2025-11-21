
from typing import List, Optional, Union
import dataclasses
import math

from pycram.enums import Arms
from pycram.task import with_tree
from pycram.plan_failures import ObjectUnfetchable, ReachabilityFailure, ObjectUndeliverable, IKError
from pycram.robot_descriptions import robot_description
from pycram.helper import multiply_quaternions, axis_angle_to_quaternion
from pycram.bullet_world import BulletWorld
from pycram.local_transformer import LocalTransformer
from pycram.designator import ActionDesignatorDescription
from pycram.designator import ObjectDesignatorDescription
from pycram.pose import Pose
from pycram.designators.object_designator import BelieveObject, ObjectPart
from pycram.designators.location_designator import CostmapLocation
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
from pycram.designators.action_designator import MoveTorsoAction, ParkArmsAction, PickUpAction, PlaceAction, NavigateAction

class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)

        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_cloth_designator.data_copy()
            object_cloth = self.object_cloth_designator.bullet_world_object

            for i, wipe_location in enumerate(self.wipe_locations):
                length = self.lengths[i]
                width = self.widths[i]
                arm = self.arms[i % len(self.arms)]

                # calculate trajectory
                def generate_trajectory(pose, length, width, gap):
                    x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                    trajectory_poses = []

                    for t in range(math.ceil(length / gap)):
                        tmp_pose = pose.copy()

                        if t % 2 == 0:
                            y = y_start + t * gap
                        else:
                            y = y_start + (t + 1) * gap

                        if y > y_start + width:
                            break

                        tmp_pose.pose.position.y = y
                        trajectoryTm = object_cloth.local_transformer.transform_pose(tmp_pose, "map")
                        trajectory_poses.append(trajectoryTm)
                        BulletWorld.current_bullet_world.add_vis_axis(trajectoryTm)

                    return trajectory_poses

                trajectory_poses = generate_trajectory(wipe_location, length, width, 0.1)

                BulletWorld.current_bullet_world.remove_vis_axis()

                # perform wiping
                for trajectory_pose in trajectory_poses:
                    # move to wiping location
                    MoveTCPMotion(trajectory_pose, arm).resolve().perform()

                    # wipe
                    MoveTCPMotion(wipe_location, arm).resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms[0])