(<- (desig:action-grounding?action-designator (close?current-object-desig?arm 
                                                         ?gripper-closing?effort 
                                                         ?left-reach-poses?right-reach-poses
                                                         ?left-close-poses?right-close-poses)
    (spec:property?action-designator (:type :closing))
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
    (-> (spec:property?action-designator (:gripper-closing?gripper-closing))
        (true)
        (and (lisp-fun obj-int:get-object-type-closing
                      ?object-type?facing-robot-face?bottom-face?rotatiationally-symmetric?arm
                      ?gripper-closings)
             (member?gripper-closing?gripper-closings)))
    (lisp-fun obj-int:get-object-type-closing-effort?object-type?effort)
    (lisp-fun obj-int:get-object-type-gripper-closing?object-type?gripper-closing)
    (lisp-fun obj-int:get-object-closing-poses
             ?object-name?object-type :left?gripper-closing?object-transform
             ?left-poses)
    (lisp-fun obj-int:get-object-closing-poses
             ?object-name?object-type :right?gripper-closing?object-transform
             ?right-poses)
    (lisp-fun extract-close-manipulation-poses?arm?