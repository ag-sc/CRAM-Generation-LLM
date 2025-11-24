(<- (desig:action-grounding?action-designator (wipe?current-object-designator?arm 
                                                       ?left-reach-poses?right-reach-poses
                                                       ?left-wipe-poses?right-wipe-poses
                                                       ?left-retract-poses?right-retract-poses
                                                       ?surface?towel))
    (spec:property?action-designator (:type :wiping))
    (-> (spec:property?action-designator (:arm?arm))
        (-> (spec:property?action-designator (:object?towel-designator))
            (or (cpoe:object-in-hand?towel-designator?arm)
                (and (format "WARNING: Wanted to wipe with towel ~a and arm ~a, ~
                              but it's not in the arm.~%"?towel-designator?arm)
                     ))
            (cpoe:object-in-hand?towel-designator?arm))
        (-> (spec:property?action-designator (:object?towel-designator))
            (cpoe:object-in-hand?towel-designator?arm)
            (and (cram-robot-interfaces:robot?robot)
                 (cram-robot-interfaces:arm?robot?arm)
                 (cpoe:object-in-hand?towel-designator?arm))))
    (once (or (cpoe:object-in-hand?towel-designator?arm)
              (spec:property?action-designator (:object?towel-designator))))
    (desig:current-designator?towel-designator?current-towel-designator)
    (spec:property?current-towel-designator (:type?towel-type))
    (spec:property?current-towel-designator (:name?towel-name))
    (obj-int:towel-type-grasp?towel-type?grasp)
    (-> (spec:property?action-designator (:target?surface))
        (and (desig:current-designator?surface?current-surface-designator)
             (desig:designator-groundings?current-surface-designator?poses)
             (member?target-pose?poses)
             (symbol-value cram-tf:*robot-base-frame*?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame?target-pose?base-frame :use-zero-time t
                      ?target