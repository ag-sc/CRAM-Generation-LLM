(<- (desig:action-grounding?action-designator (pour?source-container-designator?target-container-designator?arm 
                                                       ?left-reach-poses?right-reach-poses
                                                       ?left-pour-poses?right-pour-poses
                                                       ?left-retract-poses?right-retract-poses
                                                       ?source-location?target-location))
    (spec:property?action-designator (:type :pouring))
    (-> (spec:property?action-designator (:arm?arm))
        (-> (spec:property?action-designator (:source-container?source-container-designator))
            (or (cpoe:container-in-hand?source-container-designator?arm)
                (and (format "WARNING: Wanted to pour from container ~a with arm ~a, ~
                              but it's not in the arm.~%"?source-container-designator?arm)
                     ))
            (cpoe:container-in-hand?source-container-designator?arm))
        (-> (spec:property?action-designator (:target-container?target-container-designator))
            (cpoe:container-at-location?target-container-designator?target-location))
        (once (or (cpoe:container-in-hand?source-container-designator?arm)
                  (spec:property?action-designator (:source-container?source-container-designator))))
    (desig:current-designator?source-container-designator?current-source-container-designator)
    (spec:property?current-source-container-designator (:type?source-container-type))
    (spec:property?current-source-container-designator (:name?source-container-name))
    (obj-int:container-type-pour?source-container-type?pour-type)
    (desig:current-designator?target-container-designator?current-target-container-designator)
    (spec:property?current-target-container-designator (:type?target-container-type))
    (spec:property?current-target-container-designator (:name?target-container-name))
    (obj-int:container-type-receive?target-container-type?receive-type)
    (-> (spec:property?action-designator (:source?source-location))
        (and (desig:current-designator?source-location?current-source-location-designator)
             (desig:designator-groundings?current-source-location-designator?source-poses)
             (member?source-target-pose?source-poses)
             (symbol