
import dataclasses
from typing import List, Union
from pycram.designator import ActionDesignatorDescription
from pycram.designators.object_designator import ObjectDesignatorDescription
from pycram.pose import Pose
from pycram.task import with_tree
from pycram.designators.action_designator import PickUpAction, PlaceAction
from pycram.designators.motion_designator import MoveTCPMotion

class WipeAction(ActionDesignatorDescription):

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_cloth: ObjectDesignatorDescription.Object
        wipe_locations: List[Pose]
        lengths: List[float]
        widths: List[float]
        arms: List[str]

        @with_tree
        def perform(self) -> None:
            # Pick up the cloth
            pick_up_cloth = PickUpAction(self.object_cloth, self.arms, ["pinch"]).resolve()
            pick_up_cloth.perform()

            # Wipe the surface in a zigzag pattern
            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                # Calculate the zigzag pattern based on the length, width, and gap
                gap = 0.1  # 10 cm gap
                num_strips = int(width // gap)
                for i in range(num_strips):
                    # Calculate the start and end points of the current strip
                    start_x = wipe_location.position[0] - length / 2
                    end_x = wipe_location.position[0] + length / 2
                    y = wipe_location.position[1] + (i * gap) - (width / 2)
                    start_pose = Pose([start_x, y, wipe_location.position[2]], wipe_location.orientation)
                    end_pose = Pose([end_x, y, wipe_location.position[2]], wipe_location.orientation)

                    # Move to the start of the strip
                    move_to_start = MoveTCPMotion(start_pose, self.arms[0]).resolve()
                    move_to_start.perform()

                    # Wipe to the end of the strip
                    move_to_end = MoveTCPMotion(end_pose, self.arms[0]).resolve()
                    move_to_end.perform()

            # Place the cloth back
            place_cloth = PlaceAction(self.object_cloth, [wipe_location], self.arms).resolve()
            place_cloth.perform()

    def __init__(self, object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], wipe_locations: List[Pose], lengths: List[float], widths: List[float], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_cloth_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_cloth_description
        self.wipe_locations: List[Pose] = wipe_locations
        self.lengths: List[float] = lengths
        self.widths: List[float] = widths
        self.arms: List[str] = arms

    def ground(self) -> Action:
        object_cloth = self.object_cloth_description if isinstance(self.object_cloth_description, ObjectDesignatorDescription.Object) else self.object_cloth_description.resolve()
        return self.Action(object_cloth, self.wipe_locations, self.lengths, self.widths, self.arms)
