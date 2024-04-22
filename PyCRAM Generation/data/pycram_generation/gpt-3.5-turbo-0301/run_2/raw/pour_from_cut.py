
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

            container_location = CostmapLocation(container_pose, reachable_for=container_object)

            # Move to source object
            source_location = CostmapLocation(source_pose, reachable_for=source_object)
            MoveTCPMotion(source_location, self.arm).resolve().perform()

            # Move to container
            MoveTCPMotion(container_location, self.arm).resolve().perform()

            # Tilt source object
            tilt_pose = Pose(position=[0, 0, 0.2], orientation=[0, 0, 0, 1], frame="tcp")
            MoveTCPMotion(tilt_pose, self.arm).resolve().perform()

            # Pour
            BulletWorld.current_bullet_world.add_vis_axis(container_pose)
            start_time = time.time()
            while time.time() - start_time < self.duration:
                tilt_pose.pose.position.z -= 0.01
                MoveTCPMotion(tilt_pose, self.arm).resolve().perform()
            BulletWorld.current_bullet_world.remove_vis_axis()

            # Move back to source object
            MoveTCPMotion(source_location, self.arm).resolve().perform()

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
