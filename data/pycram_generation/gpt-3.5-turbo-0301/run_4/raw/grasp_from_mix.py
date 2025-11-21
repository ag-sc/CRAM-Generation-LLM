
from typing import List, Optional, Union
import dataclasses
from pycram.designator import ActionDesignatorDescription
from pycram.designator import ObjectDesignatorDescription
from pycram.designators.motion_designator import MoveTCPMotion, MoveGripperMotion
from pycram.robot_descriptions import robot_description
from pycram.enums import Arms

@dataclasses.dataclass
class GraspAction(ActionDesignatorDescription):
    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_designator: ObjectDesignatorDescription.Object
        arm: str
        object_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)

        @with_tree
        def perform(self) -> None:
            self.object_at_execution = self.object_designator.data_copy()
            object = self.object_designator.bullet_world_object
            obj_dim = object.get_object_dimensions()
            dim = [max(obj_dim[0], obj_dim[1]), min(obj_dim[0], obj_dim[1]), obj_dim[2]]
            obj_height = dim[2]
            oTm = object.get_pose()
            object_pose = object.local_transformer.transform_to_object_frame(oTm, object)

            # Pre-grasp position
            pre_grasp_pose = object_pose.copy()
            pre_grasp_pose.pose.position.x -= 0.1

            # Open gripper
            MoveGripperMotion("open", self.arm).resolve().perform()

            # Move to pre-grasp position
            MoveTCPMotion(pre_grasp_pose, self.arm).resolve().perform()

            # Move to grasp position
            MoveTCPMotion(object_pose, self.arm).resolve().perform()

            # Close gripper
            MoveGripperMotion("close", self.arm).resolve().perform()

    def __init__(self, object_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object, ObjectPart, ObjectPart.Object], arms: List[str], resolver=None):
        super().__init__(resolver)
        self.object_description = object_description
        self.arms = arms

    def ground(self) -> Action:
        object_desig = self.object_description if isinstance(self.object_description, ObjectDesignatorDescription.Object) else self.object_description.resolve()
        return self.Action(object_desig, self.arms[0])
