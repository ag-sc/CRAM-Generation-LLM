(<- (desig:action-grounding ?action-designator (halve-object ?arm
                                                             ?knife
                                                             ?cutting-board
                                                             ?object
                                                             ?left-reach-poses
                                                             ?right-reach-poses
                                                             ?left-cut-poses
                                                             ?right-cut-poses
                                                             ?environment-obj))
    (spec:property ?action-designator (:type :halving))
    (spec:property ?action-designator (:object ?object-designator))
    (spec:property ?object-designator (:type ?object-type))
    (obj-int:object-type-subtype :food ?object-type)
    (spec:property ?object-designator (:urdf-name ?object-name))
    (spec:property ?object-designator (:part-of ?btr-environment))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (spec:property ?action-designator (:knife ?knife))
    (spec:property ?action-designator (:cutting-board ?cutting-board))
    (btr:bullet-world ?world)
    (lisp-fun btr:object ?world ?btr-environment ?environment-obj)
    (lisp-fun get-object-pose-and-transform ?object-name ?btr-environment
              (?object-pose ?object-transform))
    (lisp-fun obj-int:get-object-cutting-poses ?object-name
              :food :left :halve ?object-transform ?left-poses)
    (lisp-fun obj-int:get-object-cutting-poses ?object-name
              :food :right :halve ?object-transform ?right-poses)
    (lisp-fun cram-mobile-pick-place-plans::extract-cutting-manipulation-poses
              ?arm ?left-poses ?right-poses
              (?left-reach-poses ?right-reach-poses
                                 ?left-cut-poses ?right-cut-poses)))