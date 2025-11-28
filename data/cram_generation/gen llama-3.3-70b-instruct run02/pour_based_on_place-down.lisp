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
             (symbol-value cram-tf:*robot-base-frame*?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame?source-target-pose?base-frame :use-zero-time t
                      ?source-target-pose-in-base)
             (lisp-fun roslisp-utilities:rosify-underscores-lisp-name?source-container-name?source-tf-name)
             (lisp-fun cram-tf:pose-stamped->transform-stamped?source-target-pose-in-base?source-tf-name
                      ?source-transform))
        (and (lisp-fun obj-int:get-container-transform?current-source-container-designator?source-transform)
             (lisp-fun obj-int:get-container-pose?current-source-container-designator?source-pose)
             (desig:designator :location ((:pose?source-pose))?source-location)))
    (-> (spec:property?action-designator (:target?target-location))
        (and (desig:current-designator?target-location?current-target-location-designator)
             (desig:designator-groundings?current-target-location-designator?target-poses)
             (member?target-target-pose?target-poses)
             (symbol-value cram-tf:*robot-base-frame*?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame?target-target-pose?base-frame :use-zero-time t
                      ?target-target-pose-in-base)
             (lisp-fun roslisp-utilities:rosify-underscores-lisp-name?target-container-name?target-tf-name)
             (lisp-fun cram-tf:pose-stamped->transform-stamped?target-target-pose-in-base?target-tf-name
                      ?target-transform))
        (and (lisp-fun obj-int:get-container-transform?current-target-container-designator?target-transform)
             (lisp-fun obj-int:get-container-pose?current-target-container-designator?target-pose)
             (desig:designator :location ((:pose?target-pose))?target-location)))
    (lisp-fun obj-int:get-container-pouring-poses
             ?source-container-name?source-container-type :left?pour-type?source-transform
             ?left-poses)
    (lisp-fun obj-int:get-container-pouring-poses
             ?source-container-name?source-container-type :right?pour-type?source-transform
             ?right-poses)
    (lisp-fun extract-pour-manipulation-poses?arm?left-poses?right-poses
              (?left-reach-poses?right-reach-poses?left-pour-poses?right-pour-poses
                                ?left-retract-poses?right-retract-poses))))