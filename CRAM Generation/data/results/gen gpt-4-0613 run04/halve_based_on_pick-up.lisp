(<- (desig:action-grounding ?action-designator (halve ?current-object-desig ?arm
                                                          ?knife ?cutting-board ?cutting-force
                                                          ?cutting-direction ?left-cut-poses ?right-cut-poses))
    (spec:property ?action-designator (:type :halving))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-transform ?current-object-desig ?object-transform)
    (lisp-fun obj-int:calculate-object-faces ?object-transform (?facing-robot-face ?bottom-face))
    (lisp-fun obj-int:get-object-type-cutting-force ?object-type ?cutting-force)
    (lisp-fun obj-int:get-object-type-cutting-direction ?object-type ?cutting-direction)
    (lisp-fun obj-int:get-object-cutting-poses
              ?object-name ?object-type :left ?cutting-direction ?object-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-cutting-poses
              ?object-name ?object-type :right ?cutting-direction ?object-transform
              ?right-poses)
    (lisp-fun extract-halving-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-cut-poses ?right-cut-poses)))