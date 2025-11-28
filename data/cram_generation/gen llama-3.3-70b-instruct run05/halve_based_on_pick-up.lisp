(<- (desig:action-grounding?action-designator (halve?current-object-desig?tool 
                                                         ?cutting-direction?cutting-effort 
                                                         ?left-approach-poses?right-approach-poses
                                                         ?left-cut-poses?right-cut-poses
                                                         ?left-retract-poses?right-retract-poses))
    (spec:property?action-designator (:type :cutting))
    (spec:property?action-designator (:object?object-designator))
    (desig:current-designator?object-designator?current-object-desig)
    (spec:property?current-object-desig (:type?object-type))
    (spec:property?current-object-desig (:name?object-name))
    (-> (spec:property?action-designator (:tool?tool))
        (true)
        (and (cram-robot-interfaces:robot?robot)
             (cram-robot-interfaces:tool?robot?tool)))
    (lisp-fun obj-int:get-object-transform?current-object-desig?object-transform)
    (lisp-fun obj-int:calculate-object-faces?object-transform (?facing-robot-face?bottom-face))
    (-> (obj-int:object-rotationally-symmetric?object-type)
        (equal?rotationally-symmetric t)
        (equal?rotationally-symmetric nil))
    (-> (spec:property?action-designator (:cutting-direction?cutting-direction))
        (true)
        (and (lisp-fun obj-int:get-object-type-cutting-directions
                      ?object-type?facing-robot-face?bottom-face?rotatiationally-symmetric
                      ?cutting-directions)
             (member?cutting-direction?cutting-directions)))
    (lisp-fun obj-int:get-object-type-cutting-effort?object-type?cutting-effort)
    (lisp-fun obj-int:get-object-grasping-poses
             ?object-name?object-type :left?cutting-direction?object-transform
             ?left-approach-poses)
    (lisp-fun obj-int:get-object-grasping-poses
             ?object-name?object-type :right?cutting-direction?object-transform
             ?right-approach-poses)
    (lisp-fun extract-halve-manipulation-poses?tool?left-approach-poses?right-approach-poses
              (?left-cut-poses?right-cut-poses
                                ?left-retract-poses?right-retract-poses)))