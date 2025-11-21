
import dataclasses
from typing import List, Union
from pycram.designator import ActionDesignatorDescription
from pycram.designators.object_designator import ObjectDesignatorDescription
from pycram.pose import Pose
from pycram.task import with_tree
from pycram.designators.motion_designator import MoveTCPMotion
from pycram.robot_descriptions import robot_description
from pycram.bullet_world import BulletWorld
from pycram.local_transformer import LocalTransformer

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
            bullet_world = BulletWorld.get_bullet_world()
            local_transformer = LocalTransformer.get_local_transformer()
            gripper = robot_description.i.get_gripper_for_arm(self.arms[0])

            # Pick up the cloth
            cloth_pose = bullet_world.get_object_position(self.object_cloth.name)
            pick_cloth_motion = MoveTCPMotion(target=Pose(position=cloth_pose[0], orientation=cloth_pose[1]), arm=self.arms[0])
            pick_cloth_motion.resolve().perform()

            # Wipe the surface in a zigzag pattern
            for wipe_location, length, width in zip(self.wipe_locations, self.lengths, self.widths):
                # Calculate the number of strips based on the width and the gap
                num_strips = int(width / 0.1)
                strip_length = length / num_strips
                for i in range(num_strips):
                    # Calculate the start and end points of the strip
                    start_x = wipe_location.position[0] - (length / 2) + (i * strip_length)
                    end_x = start_x + strip_length
                    start_pose = Pose(position=[start_x, wipe_location.position[1], wipe_location.position[2]], orientation=wipe_location.orientation)
                    end_pose = Pose(position=[end_x, wipe_location.position[1], wipe_location.position[2]], orientation=wipe_location.orientation)

                    # Move to the start of the strip
                    move_to_start = MoveTCPMotion(target=start_pose, arm=self.arms[0])
                    move_to_start.resolve().perform()

                    # Wipe to the end of the strip
                    move_to_end = MoveTCPMotion(target=end_pose, arm=self.arms[0])
                    move_to_end.resolve().perform()

            # Release the cloth
            release_cloth_motion = MoveTCPMotion(target=Pose(position=cloth_pose[0], orientation=cloth_pose[1]), arm=self.arms[0], allow_gripper_collision=True)
            release_cloth_motion.resolve().perform()

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
