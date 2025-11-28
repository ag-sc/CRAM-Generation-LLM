(<- (desig:action-grounding?action-designator (wipe?current-object-desig?arm 
                                                         ?gripper-opening?effort?wiping-tool
                                                         ?left-wipe-poses?right-wipe-poses
                                                         ?left-wipe-orientations?right-wipe-orientations)
    (spec:property?action-designator (:type :wiping))
    (spec:property?action-designator (:surface?surface-designator))
    (desig:current-designator?surface-designator?current-object-desig)
    (spec:property?current-object-desig (:type?surface-type))
    (spec:property?current-object-desig (:name?surface-name))
    (-> (spec:property?action-designator (:arm?arm))
        (true)
        (and (cram-robot-interfaces:robot?robot)
             (cram-robot-interfaces:arm?robot?arm)))
    (lisp-fun obj-int:get-surface-transform?current-object-desig?surface-transform)
    (lisp-fun obj-int:calculate-surface-normal?surface-transform (?surface-normal))
    (-> (spec:property?action-designator (:wiping-tool?wiping-tool))
        (true)
        (and (lisp-fun obj-int:get-surface-wiping-tools
                      ?surface-type?arm
                      ?wiping-tools)
             (member?wiping-tool?wiping-tools)))
    (lisp-fun obj-int:get-surface-wiping-effort?surface-type?effort)
    (lisp-fun obj-int:get-surface-wiping-gripper-opening?surface-type?gripper-opening)
    (lisp-fun obj-int:get-surface-wiping-poses
             ?surface-name?surface-type :left?wiping-tool?surface-transform
             ?left-poses)
    (lisp-fun obj-int:get-surface-wiping-poses
             ?surface-name?surface-type :right?wiping-tool?surface-transform
             ?right-poses)
    (lisp-fun obj-int:get-surface-wiping-orientations
             ?surface-name?surface-type :left?wiping-tool?surface-transform
             ?left-orientations)
    (lisp-fun obj-int:get-surface-wiping-orientations
             ?surface-name?surface-type :right?wiping-tool?surface-transform
             ?right-orientations)
    (lisp-fun extract-wipe-manipulation-poses?arm?left-poses?right-poses 
             ?left-orientations?right-orientations
              (?left-wipe-poses?right-wipe-poses 
                                ?left-wipe-orientations?right-wipe-orientations)))