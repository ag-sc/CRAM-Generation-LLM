(<- (desig:action-grounding?action-designator (hold?current-object-desig?arm 
                                                         ?gripper-closure?effort 
                                                         ?left-hold-poses?right-hold-poses)
    (spec:property?action-designator (:type :holding))
    (spec:property?action-designator (:object?object-designator))
    (desig:current-designator?object-designator?current-object-desig)
    (spec:property?current-object-desig (:type?object-type))
    (spec:property?current-object-desig (:name?object-name))
    (-> (spec:property?action-designator (:arm?arm))
        (true)
        (and (cram-robot-interfaces:robot?robot)
             (cram-robot-interfaces:arm?robot?arm)))
    (lisp-fun obj-int:get-object-transform?current-object-desig?object-transform)
    (lisp-fun obj-int:calculate-object-faces?object-transform (?facing-robot-face?bottom-face))
    (-> (obj-int:object-rotationally-symmetric?object-type)
        (equal?rotationally-symmetric t)
        (equal?rotationally-symmetric nil))
    (-> (spec:property?action-designator (:gripper-closure?gripper-closure))
        (true)
        (and (lisp-fun obj-int:get-object-type-gripping-effort 
                      ?object-type?effort)
             (lisp-fun obj-int:get-object-type-gripper-closure 
                      ?object-type?gripper-closure)))
    (lisp-fun obj-int:get-object-type-holding-poses
             ?object-name?object-type :left?object-transform
             ?left-hold-poses)
    (lisp-fun obj-int:get-object-type-holding-poses
             ?object-name?object-type :right?object-transform
             ?right-hold-poses)
    (lisp-fun extract-hold-manipulation-poses?arm?left-hold-poses?right-hold-poses
              (?left-hold-poses?right-hold-poses)))