
from typing import List, Union
import dataclasses
import numpy as np

from pycram.designator import ActionDesignatorDescription, ObjectDesignatorDescription
from pycram.designators.motion_designator import MoveTCPMotion
from pycram.designators.action_designator import NavigateAction
from pycram.robot_descriptions import robot_description
from pycram.bullet_world import BulletWorld
from pycram.pose import Pose

class WipeAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth_designator: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]

        def perform(self) -> None:
            cloth_object = self.object_cloth_designator.bullet_world_object
            cloth_pose = cloth_object.get_pose()
            cloth_dim = cloth_object.get_object_dimensions()

            for i, wipe_location in enumerate(self.wipe_locations):
                length = self.lengths[i]
                width = self.widths[i]
                arm = self.arms[i % len(self.arms)]

                # Calculate the number of strips
                num_strips = int(length / 0.1)

                # Calculate the starting position of the wipe
                start_pos = np.array([wipe_location.pose.position.x - length / 2, wipe_location.pose.position.y - width / 2, wipe_location.pose.position.z])

                # Calculate the direction of the wipe
                direction = np.array([1, 0, 0])

                # Calculate the distance between each strip
                strip_distance = length / num_strips

                # Calculate the gap between each strip
                gap = 0.1

                # Calculate the height of the cloth object
                cloth_height = cloth_dim[2]

                # Move the arm to the starting position
                start_pose = Pose(position=start_pos, frame="map")
                MoveTCPMotion(start_pose, arm).resolve().perform()

                # Wipe in a zigzag pattern
                for j in range(num_strips):
                    # Calculate the position of the current strip
                    strip_pos = start_pos + j * strip_distance * direction

                    # Calculate the position of the next strip
                    next_strip_pos = strip_pos + strip_distance * direction

                    # Calculate the position of the gap between the strips
                    gap_pos = strip_pos + (strip_distance - gap) * direction

                    # Move the arm to the current strip position
                    strip_pose = Pose(position=strip_pos, frame="map")
                    MoveTCPMotion(strip_pose, arm).resolve().perform()

                    # Move the arm down to the cloth object
                    cloth_pose.pose.position.z = cloth_height
                    MoveTCPMotion(cloth_pose, arm).resolve().perform()

                    # Move the arm up to the gap position
                    gap_pose = Pose(position=gap_pos, frame="map")
                    MoveTCPMotion(gap_pose, arm).resolve().perform()

                    # Move the arm down to the cloth object
                    cloth_pose.pose.position.z = cloth_height
                    MoveTCPMotion(cloth_pose, arm).resolve().perform()

                # Move the arm to the starting position
                MoveTCPMotion(start_pose, arm).resolve().perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description = object_cloth_description
        self.wipe_locations = wipe_locations
        self.lengths = lengths
        self.widths = widths
        self.arms = arms

    def ground(self) -> Action:
        object_cloth_desig = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth_desig, self.wipe_locations, self.lengths, self.widths, self.arms)