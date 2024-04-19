
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

            obj_dim = object_cloth.get_object_dimensions()
            dim = [max(obj_dim[0], obj_dim[1]), min(obj_dim[0], obj_dim[1]), obj_dim[2]]
            obj_height = dim[2]
            oTm = object_cloth.get_pose()
            object_cloth_pose = object_cloth.local_transformer.transform_to_object_frame(oTm, object_cloth)

            def generate_wipe_trajectory(pose, length, width, gap):
                x_start, y_start, z_start = pose.pose.position.x, pose.pose.position.y, pose.pose.position.z
                wipe_poses = []

                for i in range(int(length/gap)):
                    tmp_pose = pose.copy()

                    if i % 2 == 0:
                        y = y_start + i * gap
                    else:
                        y = y_start + (i+1) * gap

                    for j in range(int(width/gap)):
                        if j % 2 == 0:
                            x = x_start + j * gap
                        else:
                            x = x_start + (j+1) * gap

                        tmp_pose.pose.position.x = x
                        tmp_pose.pose.position.y = y
                        wipeTm = object_cloth.local_transformer.transform_pose(tmp_pose, "map")
                        wipe_poses.append(wipeTm)
                        BulletWorld.current_bullet_world.add_vis_axis(wipeTm)

                return wipe_poses

            wipe_poses = []
            for i in range(len(self.wipe_locations)):
                wipe_poses += generate_wipe_trajectory(self.wipe_locations[i], self.lengths[i], self.widths[i], 0.1)

            BulletWorld.current_bullet_world.remove_vis_axis()

            for wipe_pose in wipe_poses:
                oriR = axis_angle_to_quaternion([1, 0, 0], 180)
                ori = multiply_quaternions([wipe_pose.orientation.x, wipe_pose.orientation.y, wipe_pose.orientation.z, wipe_pose.orientation.w], oriR)
                adjusted_wipe_pose = wipe_pose.copy()
                adjusted_wipe_pose.orientation.x = ori[0]
                adjusted_wipe_pose.orientation.y = ori[1]
                adjusted_wipe_pose.orientation.z = ori[2]
                adjusted_wipe_pose.orientation.w = ori[3]

                lift_pose = adjusted_wipe_pose.copy()
                lift_pose.pose.position.z += (obj_height + 0.08)
                MoveTCPMotion(lift_pose, self.arms[0]).resolve().perform()

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
