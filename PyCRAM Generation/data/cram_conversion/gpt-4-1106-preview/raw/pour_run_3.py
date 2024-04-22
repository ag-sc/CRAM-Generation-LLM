
import dataclasses
from typing import List, Union
from pycram.designator import ActionDesignatorDescription, ObjectDesignatorDescription
from pycram.task import with_tree
from pycram.robot_descriptions import robot_description
from pycram.pose import Pose
from pycram.designators.motion_designator import MoveTCPMotion
from pycram.designators.action_designator import PickUpAction, PlaceAction

class PourAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source: ObjectDesignatorDescription.Object
        object_container: ObjectDesignatorDescription.Object
        arms: List[str]
        durations: List[float]

        @with_tree
        def perform(self) -> None:
            # Pick up the source object
            pickup_action = PickUpAction(self.object_source, self.arms).resolve()
            pickup_action.perform()

            # Calculate the pose for pouring
            container_pose = self.object_container.get_pose()
            pour_pose = Pose(position=[container_pose.position[0], container_pose.position[1], container_pose.position[2] + 0.2],
                             orientation=[0, 0, 0, 1],  # Assuming that the robot's default orientation is correct for pouring
                             frame=container_pose.frame)

            # Move the TCP to the pouring pose
            move_tcp_action = MoveTCPMotion(pour_pose, self.arms[0]).resolve()
            move_tcp_action.perform()

            # Perform the pouring action by tilting the source object
            # Assuming that the robot has a method to tilt the object by 90 degrees
            robot_description.get_robot().tilt_gripper(90, self.arms[0])

            # Wait for the specified duration to pour
            time.sleep(self.durations[0])

            # Return the source object to its original orientation
            robot_description.get_robot().tilt_gripper(-90, self.arms[0])

            # Place the source object back to its original location or a designated place
            place_action = PlaceAction(self.object_source, [self.object_source.get_pose()], self.arms).resolve()
            place_action.perform()

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
