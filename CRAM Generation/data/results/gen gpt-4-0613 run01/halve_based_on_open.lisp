(<- (desig:action-grounding ?action-designator (halve-object ?arm
                                                             ?knife
                                                             ?cutting-board
                                                             ?object
                                                             ?left-reach-poses
                                                             ?right-reach-poses
                                                             ?left-cut-poses
                                                             ?right-cut-poses
                                                             (?left-lift-pose)
                                                             (?right-lift-pose)
                                                             (?left-2nd-lift-pose)
                                                             (?right-2nd-lift-pose)
                                                             ?joint-name ?environment-obj))
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
                                 ?left-cut-poses ?right-cut-poses
                                 ?left-lift-poses ?right-lift-poses))
     (-> (lisp-pred identity ?left-lift-poses)
        (equal ?left-lift-poses (?left-lift-pose ?left-2nd-lift-pose))
        (equal (NIL NIL) (?left-lift-pose ?left-2nd-lift-pose)))
    (-> (lisp-pred identity ?right-lift-poses)
        (equal ?right-lift-poses (?right-lift-pose ?right-2nd-lift-pose))
        (equal (NIL NIL) (?right-lift-pose ?right-2nd-lift-pose))))