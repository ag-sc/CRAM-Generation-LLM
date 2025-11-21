
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

class PourAction(ActionDesignatorDescription):
    """
    Designator to let the robot perform a pouring action.
    """

    @dataclasses.dataclass
    class Action(ActionDesignatorDescription.Action):
        object_source_designator: ObjectDesignatorDescription.Object
        """
        Object designator describing the source object that should be poured.
        """

        object_container_designator: ObjectDesignatorDescription.Object
        """
        Object designator describing the container where the source object should be poured into.
        """

        arm: str
        """
        The arm that should be used for pouring.
        """

        duration: float
        """
        The duration of the pouring action in seconds.
        """

        object_source_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        """
        The source object at the time this Action got created. It is used to be a static, information holding entity. It is
        not updated when the BulletWorld object is changed.
        """

        object_container_at_execution: Optional[ObjectDesignatorDescription.Object] = dataclasses.field(init=False)
        """
        The container object at the time this Action got created. It is used to be a static, information holding entity. It is
        not updated when the BulletWorld object is changed.
        """

        @with_tree
        def perform(self) -> None:
            """
            Perform the pouring action using the specified source object, container, arm, and duration.
            """
            # Store the object's data copy at execution
            self.object_source_at_execution = self.object_source_designator.data_copy()
            self.object_container_at_execution = self.object_container_designator.data_copy()

            # Retrieve objects and robot from designators
            source_object = self.object_source_designator.bullet_world_object
            container_object = self.object_container_designator.bullet_world_object

            # Get dimensions of objects
            source_dim = source_object.get_object_dimensions()
            container_dim = container_object.get_object_dimensions()

            # Get poses of objects
            sTm = source_object.get_pose()
            cTm = container_object.get_pose()

            # Calculate target pose for source object
            target_pose = Pose(position=[cTm.pose.position.x, cTm.pose.position.y, cTm.pose.position.z + container_dim[2]/2 + 0.2], orientation=[0, 0, 0, 1], frame="map")

            # Move to source object
            MoveTCPMotion(sTm, self.arm).resolve().perform()

            # Pick up source object
            PickUpAction(self.object_source_designator, [self.arm], ["top"], resolver=None).resolve().perform()

            # Move to container
            PlaceAction(self.object_container_designator, [target_pose], [self.arm], resolver=None).resolve().perform()

            # Calculate target pose for pouring
            pour_pose = Pose(position=[cTm.pose.position.x, cTm.pose.position.y, cTm.pose.position.z + container_dim[2]/2 + 0.2], orientation=[0, 0, 1, 0], frame="map")

            # Move to pouring pose
            MoveTCPMotion(pour_pose, self.arm).resolve().perform()

            # Open gripper
            MoveGripperMotion("open", self.arm).resolve().perform()

            # Perform pouring action
            time.sleep(self.duration)

            # Close gripper
            MoveGripperMotion("close", self.arm).resolve().perform()

            # Move back to source object
            MoveTCPMotion(sTm, self.arm).resolve().perform()

            # Place source object back
            PlaceAction(self.object_source_designator, [sTm], [self.arm], resolver=None).resolve().perform()

    def __init__(self, object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object], arms: List[str], durations: List[float], resolver=None):
        """
        Initialize the PourAction with object designators, arms, and durations.

        :param object_source_description: Object designator description or Object designator for the source object to be poured.
        :param object_container_description: Object designator description or Object designator for the container where the source object should be poured into.
        :param arms: List of possible arms that could be used.
        :param durations: List of possible durations for the pouring action.
        :param resolver: An optional resolver for dynamic parameter selection.
        """
        super().__init__(resolver)
        self.object_source_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_source_description
        self.object_container_description: Union[ObjectDesignatorDescription, ObjectDesignatorDescription.Object] = object_container_description
        self.arms: List[str] = arms
        self.durations: List[float] = durations

    def ground(self) -> Action:
        """
        Default resolver, returns a performable designator with the first entries from the lists of possible parameter.

        :return: A performable designator
        """
        object_source_desig = self.object_source_description if isinstance(self.object_source_description, ObjectDesignatorDescription.Object) else self.object_source_description.resolve()
        object_container_desig = self.object_container_description if isinstance(self.object_container_description, ObjectDesignatorDescription.Object) else self.object_container_description.resolve()
        return self.Action(object_source_desig, object_container_desig, self.arms[0], self.durations[0])
