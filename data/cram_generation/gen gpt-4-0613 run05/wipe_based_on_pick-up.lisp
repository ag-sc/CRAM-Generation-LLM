(<- (desig:action-grounding ?action-designator (wipe ?current-object-desig ?arm
                                                      ?towel ?wipe-method ?wipe-direction
                                                      ?left-wipe-poses ?right-wipe-poses))
    (spec:property ?action-designator (:type :wiping))
    (spec:property ?action-designator (:object ?object-designator))
    (desig:current-designator ?object-designator ?current-object-desig)
    (spec:property ?current-object-desig (:type ?object-type))
    (spec:property ?current-object-desig (:name ?object-name))
    (-> (spec:property ?action-designator (:arm ?arm))
        (true)
        (and (cram-robot-interfaces:robot ?robot)
             (cram-robot-interfaces:arm ?robot ?arm)))
    (lisp-fun obj-int:get-object-transform ?current-object-desig ?object-transform)
    (-> (spec:property ?action-designator (:towel ?towel))
        (true)
        (and (lisp-fun obj-int:get-object-type-towels
                       ?object-type ?towel)
             (member ?towel ?towels)))
    (-> (spec:property ?action-designator (:wipe-method ?wipe-method))
        (true)
        (and (lisp-fun obj-int:get-object-type-wipe-methods
                       ?object-type ?wipe-method)
             (member ?wipe-method ?wipe-methods)))
    (-> (spec:property ?action-designator (:wipe-direction ?wipe-direction))
        (true)
        (and (lisp-fun obj-int:get-object-type-wipe-directions
                       ?object-type ?wipe-direction)
             (member ?wipe-direction ?wipe-directions)))
    (lisp-fun obj-int:get-object-wiping-poses
              ?object-name ?object-type :left ?wipe-method ?wipe-direction ?object-transform
              ?left-poses)
    (lisp-fun obj-int:get-object-wiping-poses
              ?object-name ?object-type :right ?wipe-method ?wipe-direction ?object-transform
              ?right-poses)
    (lisp-fun extract-wipe-manipulation-poses ?arm ?left-poses ?right-poses
              (?left-wipe-poses ?right-wipe-poses)))