(<- (desig:action-grounding?action-designator (open?container-designator?arm 
                                                       ?left-reach-poses?right-reach-poses
                                                       ?left-open-poses?right-open-poses
                                                       ?left-retract-poses?right-retract-poses))
    (spec:property?action-designator (:type :opening))
    (-> (spec:property?action-designator (:arm?arm))
        (-> (spec:property?action-designator (:container?container-designator))
            (cpoe:container-closed?container-designator)
            (and (cram-robot-interfaces:robot?robot)
                 (cram-robot-interfaces:arm?robot?arm)
                 (cpoe:container-in-reach?container-designator?arm))))
    (once (or (cpoe:container-in-reach?container-designator?arm)
              (spec:property?action-designator (:container?container-designator))))
    (desig:current-designator?container-designator?current-container-designator)
    (spec:property?current-container-designator (:type?container-type))
    (spec:property?current-container-designator (:name?container-name))
    (obj-int:container-type-open?container-type?open-type)
    (-> (spec:property?action-designator (:target?container-designator))
        (and (desig:current-designator?container-designator?current-container-designator)
             (desig:designator-groundings?current-container-designator?poses)
             (member?target-pose?poses)
             (symbol-value cram-tf:*robot-base-frame*?base-frame)
             (lisp-fun cram-tf:ensure-pose-in-frame?target-pose?base-frame :use-zero-time t
                      ?target-pose-in-base)
             (lisp-fun roslisp-utilities:rosify-underscores-lisp-name?container-name?tf-name)
             (lisp-fun cram-tf:pose-stamped->transform-stamped?target-pose-in-base?tf-name
                      ?target-transform))
        (and (lisp-fun obj-int:get-container-transform?current-container-designator?target-transform)
             (lisp-fun obj-int:get-container-pose?current-container-designator?target-pose)
             (desig:designator :container ((:pose?target-pose))?container-designator)))
    (lisp-fun obj-int:get-container-opening-poses
             ?container-name?container-type :left?open-type?target-transform
             ?left-poses)
    (lisp-fun obj-int:get-container-opening-poses
             ?container-name?container-type :right?open-type?target-transform
             ?right-poses)
    (lisp-fun extract-open-manipulation-poses?arm?left-poses?right-poses
              (?left-reach-poses?right-reach-poses?left-open-poses?right-open-poses
                                ?left-retract-poses?right-retract-poses))))