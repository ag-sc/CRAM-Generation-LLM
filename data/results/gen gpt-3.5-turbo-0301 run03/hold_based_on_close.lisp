(<- (desig:action-grounding ?action-designator (hold ?arm
                                                      ?gripper-opening
                                                      ?object-designator))
    (spec:property ?action-designator (:type :holding))
    (spec:property ?action-designator (:object ?object-designator))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-type-gripper-opening
              (spec:property ?object-designator (:type ?object-type))
              ?gripper-opening)
    (spec:property ?object-designator (:part-of ?environment))
    (lisp-fun cram-robot-interfaces:get-object-pose ?object-designator ?object-pose)
    (lisp-fun cram-robot-interfaces:get-object-transform ?object-designator ?object-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-pose ?arm ?gripper-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-transform ?arm ?gripper-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-joint ?arm ?gripper-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-link ?arm ?gripper-link)
    (lisp-fun cram-robot-interfaces:get-gripper-frame ?arm ?gripper-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?gripper-base-transform)
    (lisp-fun cram-robot-interfaces:get-gripper-base-frame ?arm ?gripper-base-frame)
    (lisp-fun cram-robot-interfaces:get-gripper-base-pose ?arm ?gripper-base-pose)
    (lisp-fun cram-robot-interfaces:get-gripper-base-joint ?arm ?gripper-base-joint)
    (lisp-fun cram-robot-interfaces:get-gripper-base-link ?arm ?gripper-base-link)
    (lisp-fun cram-robot-interfaces:get-gripper-base-transform ?arm ?g