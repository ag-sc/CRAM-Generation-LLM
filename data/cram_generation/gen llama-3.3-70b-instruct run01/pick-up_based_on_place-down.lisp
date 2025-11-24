(<- (desig:action-grounding?action-designator (pick-up?object-designator?arm 
                                                       ?left-reach-poses?right-reach-poses
                                                       ?left-grasp-poses?right-grasp-poses
                                                       ?left-lift-poses?right-lift-poses))
    (spec:property?action-designator (:type :picking))
    (-> (spec:property?action-designator (:arm?arm))
        (-> (spec:property?action-designator (:object?object-designator))
            (not (cpoe:object-in-hand?object-designator?arm))
            (and (format "WARNING: Wanted to pick up an object ~a with arm ~a, ~
                          but it's already in the arm.~%"?object-designator?arm)
                 ))
            (not (cpoe:object-in-hand?object-designator?arm)))
        (-> (spec:property?action-designator (:object?object-designator))
            (not (cpoe:object-in-hand?object-designator?arm))
            (and (cram-robot-interfaces:robot?robot)
                 (cram-robot-interfaces:arm?robot?arm)
                 (not (cpoe:object-in-hand?object-designator?arm))))
    (once (or (not (cpoe:object-in-hand?object-designator?arm))
              (spec:property?action-designator (:object?object-designator))))
    (desig:current-designator?object-designator?current-object-designator)
    (spec:property?current-object-designator (:type?object-type))
    (spec:property?current-object-designator (:name?object-name))
    (obj-int:object-type-grasp?object-type?grasp)
    (-> (spec:property?action-designator (:target?location))
        (and (desig:current-designator?location?current-location-designator)
             (desig:designator-groundings?current-location-designator?poses)
             (member?target-pose?poses)
             (symbol-value cram-tf:*robot-base-frame*?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame?target-pose?base-frame :use-zero-time t
                      ?target-pose-in-base)
             (lisp-fun roslisp-utilities