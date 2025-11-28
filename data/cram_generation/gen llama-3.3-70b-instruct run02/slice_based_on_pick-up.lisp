(<- (desig:action-grounding?action-designator (slice?current-object-desig?arm 
                                                         ?gripper-opening?effort?knife 
                                                         ?left-approach-poses?right-approach-poses
                                                         ?left-slice-poses?right-slice-poses
                                                         ?left-retract-poses?right-retract-poses))
    (spec:property?action-designator (:type :slicing))
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
    (-> (spec:property?action-designator (:knife?knife))
        (true)
        (and (lisp-fun obj-int:get-object-type-knives
                      ?object-type?facing-robot-face?bottom-face?rotatiationally-symmetric?arm
                      ?knives)
             (member?knife?knives)))
    (lisp-fun obj-int:get-object-type-slicing-effort?object-type?effort)
    (lisp-fun obj-int:get-object-type-gripper-opening?object-type?gripper-opening)
    (lisp-fun obj-int:get-object-slicing-poses
             ?object-name?object-type :left?knife?object-transform
             ?left-poses)
    (lisp-fun obj-int:get-object-slicing-poses
             ?object-name?object-type :right?knife?object-transform
             ?right-poses)
    (lisp-fun extract-slice-manipulation-poses?arm?left-poses?right-poses
              (?left-approach-poses?right-approach-poses
                                ?left-slice-poses?right-slice-poses
                                ?left-retract-poses?right-retract-poses)))