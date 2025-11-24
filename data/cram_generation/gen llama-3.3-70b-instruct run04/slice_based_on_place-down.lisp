(<- (desig:action-grounding?action-designator (slice?current-object-designator?arm 
                                                       ?left-reach-poses?right-reach-poses
                                                       ?left-slice-poses?right-slice-poses
                                                       ?left-retract-poses?right-retract-poses
                                                       ?location?cutting-direction))
    (spec:property?action-designator (:type :slicing))
    (-> (spec:property?action-designator (:arm?arm))
        (-> (spec:property?action-designator (:object?object-designator))
            (or (cpoe:object-in-hand?object-designator?arm)
                (and (format "WARNING: Wanted to slice an object ~a with arm ~a, ~
                              but it's not in the arm.~%"?object-designator?arm)
                     ))
            (cpoe:object-in-hand?object-designator?arm))
        (-> (spec:property?action-designator (:object?object-designator))
            (cpoe:object-in-hand?object-designator?arm)
            (and (cram-robot-interfaces:robot?robot)
                 (cram-robot-interfaces:arm?robot?arm)
                 (cpoe:object-in-hand?object-designator?arm))))
    (once (or (cpoe:object-in-hand?object-designator?arm)
              (spec:property?action-designator (:object?object-designator))))
    (desig:current-designator?object-designator?current-object-designator)
    (spec:property?current-object-designator (:type?object-type))
    (spec:property?current-object-designator (:name?object-name))
    (obj-int:object-type-cut?object-type?cutting-direction)
    (-> (spec:property?action-designator (:target?location))
        (and (desig:current-designator?location?current-location-designator)
             (desig:designator-groundings?current-location-designator?poses)
             (member?target-pose?poses)
             (symbol-value cram-tf:*robot-base-frame*?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame?target-pose?base-frame :use-zero-time t
                      ?target-pose-in-base)
             (lisp-fun roslisp-utilities: