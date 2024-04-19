
from typing import List, Optional, Union
import dataclasses
import numpy as np

from pycram.designator import ActionDesignatorDescription
from pycram.designator import ObjectDesignatorDescription
from pycram.robot_descriptions import robot_description
from pycram.task import with_tree
from pycram.bullet_world import BulletWorld
from pycram.helper import multiply_quaternions, axis_angle_to_quaternion
from pycram.pose import Pose
from pycram.enums import Arms
from pycram.designators.motion_designator import MoveTCPMotion
from pycram.designators.location_designator import CostmapLocation

class PourAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        object_container_designator: ObjectDesignatorDescription.Object
        arm: str
        duration: float
        object_source_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)
        object_container_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False, repr=False)

        @with_tree
        def perform(self) -> None:
            self.object_source_at_execution = self.object_source_designator.data_copy()
            self.object_container_at_execution = self.object_container_designator.data_copy()

            source_object = self.object_source_designator.bullet_world_object
            container_object = self.object_container_designator.bullet_world_object

            source_dim = source_object.get_object_dimensions()
            container_dim = container_object.get_object_dimensions()

            source_pose = source_object.get_pose()
            container_pose = container_object.get_pose()

            source_pose = source_object.local_transformer.transform_to_object_frame(source_pose, source_object)
            container_pose = container_object.local_transformer.transform_to_object_frame(container_pose, container_object)

            source_height = source_dim[2]
            container_height = container_dim[2]

            source_pose.pose.position.z += source_height / 2
            container_pose.pose.position.z += container_height / 2

            container_location = CostmapLocation(container_pose, reachable_for=container_object, visible_for=container_object, reachable_arm=self.arm).resolve()

            # Move to source object
            source_location = CostmapLocation(source_pose, reachable_for=source_object, visible_for=source_object, reachable_arm=self.arm).resolve()
            MoveTCPMotion(source_location, self.arm).resolve().perform()

            # Move to container
            MoveTCPMotion(container_location, self.arm).resolve().perform()

            # Tilt source object
            tilt_pose = Pose(position=[0, 0, source_height / 2 + 0.2], orientation=[0, 0, 0, 1], frame=source_pose.frame)
            tilt_pose = source_object.local_transformer.transform_to_object_frame(tilt_pose, source_object)
            tilt_pose = multiply_quaternions([tilt_pose.orientation.x, tilt_pose.orientation.y, tilt_pose.orientation.z, tilt_pose.orientation.w], [0, 0, 1, np.pi / 2])
            tilt_pose = Pose(position=[0, 0, container_height / 2], orientation=tilt_pose, frame=container_pose.frame)
            MoveTCPMotion(tilt_pose, self.arm).resolve().perform()

            # Pour for duration
            time.sleep(self.duration)

            # Move back to source object
            MoveTCPMotion(container_location, self.arm).resolve().perform()
            MoveTCPMotion(source_location, self.arm).resolve().perform()

            # Tilt source object back
            MoveTCPMotion(source_pose, self.arm).resolve().perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        super().__init__(resolver)
        self.object_source_description = object_source_description
        self.object_container_description = object_container_description
        self.arms = arms
        self.durations = durations

    def ground(self) -> Action:
        object_source = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source, object_container, self.arms[0], self.durations[0])
