"""
author: Jose N. Molina

twitter: @jnmation

description:

    Tools for working with keyframes on the timeline and in the Graph Editor.

    Move:           Moves the selected keyframe(s) (on the timeline or in the Graph Editor).
                    If any channels are selected, it only moves the key(s) on those channels.

                    Set these as hotkeys and it moves the selected keyframe or selected range of keyframes.
                    If the tool window is open, it takes the value from the slider, otherwise it defaults to 1.
                    import jnm_keyswin;jnm_keyswin.moveKeys('left')
                    import jnm_keyswin;jnm_keyswin.moveKeys('right')

    Re-time:        Based on the first selected key on the timeline, the range of selected keys are re-timed by the number selected in the UI.
                    If any channels are selected, it only re-times the key(s) on those channels.

                    If used as a shelf button, it creates a small window with a slider and the Re-time button.

                    Standalone tool window:

                    import jnm_keyswin;jnm_keyswin.retimewin()

    Set/Select:     Sets/Select keys every number of frames between two selected keyframes. Number taken from UI selected value.
                    If any animation layers exist, you must also select the curves animation layer.

                    If used as a shelf button, it creates a small window with a slider and the Set/Select buttons.

                    Standalone tool window:

                    import jnm_keyswin;jnm_keyswin.setselWin()

"""
author = 'Jose N. Molina'
version = 1
website = 'https://jnmolina.wordpress.com/tools'

import maya.cmds as mc
import maya.mel as mm
from maya import OpenMaya

# uses Morgan Loomis' ml_utilities http://morganloomis.com/tool/ml_utilities/
import ml_utilities as ml

# JNM scripts
def displayWarning(text):
    return OpenMaya.MGlobal.displayWarning(text)

def getTime(*args):
    return mc.currentTime(query=True)

def objSelected(*args):
    sel = mc.ls(sl=True)
    if sel:
        return sel
    else:
        displayWarning('Nothing selected.')

def getStepTime(*args):
    global step
    return mc.intSliderGrp(step,query=True,value=True)

gPlayBackSlider = mm.eval('$temp=$gPlayBackSlider')

# get the selected range
def getSeletedRange(start, end):
    pbRange = mc.timeControl(gPlayBackSlider, query=True, rangeArray=True)
    start = float(pbRange[0])
    end = float(pbRange[1])
    return start,end

# get the timeslider min/max
def getpbRange(start, end):
    start = mc.playbackOptions(query=True, min=True)
    end = mc.playbackOptions(query=True, max=True)
    return start,end

# check if a curve key is selected
def checkKeysSelected(*args):
    keyCount = mc.keyframe(query=True, keyframeCount=True)
    if keyCount:
        pass
    else:
        displayWarning('No keys in selected range.')

# check if a key exists for the given frame
def keyExists(t,channel=None):
    if channel != None :
        if mc.keyframe(query=True,time=(t,),at=channel) == None:
            return False
        else:
            return True
    else:
        if mc.keyframe(query=True,time=(t,)) == None:
            return False
        else:
            return True

# get frames that have keyframes
def getKeysInRange(start,end,channel=None):
    keys = []
    mc.refresh(suspend=True)
    for x in range(int(start),int(end)):
        if channel != None :
            if keyExists(x,channel):
                keys.append(int(x))
        else:
            if keyExists(x):
                keys.append(int(x))
    mc.refresh(suspend=False)
    return keys

# check if timeline range is selected
def checkRangeSelected(*args):
    if mc.timeControl(gPlayBackSlider, query=True, rangeVisible=True):
        return True
    else:
        return False

# get curve keyframes selected
def keyCount(*args):
    count = mc.keyframe(query=True, timeChange=True, selected=True)
    return count

# Move timeline keys
def moveKey(time,new_time,option,channel=None):
        mc.refresh(suspend=True)
        if channel != None :
            mc.keyframe(edit=True,time=(time,),option=option,timeChange=int(new_time),at=channel)
        else:
            mc.keyframe(edit=True,time=(time,),option=option,timeChange=int(new_time))
        mc.refresh(suspend=False)

# Move selected keys in Graph Editor
def moveSelectedKeys(step):
        mc.refresh(suspend=True)
        mc.keyframe(edit=True,animation='keysOrObjects',option='move',relative=True,timeChange=int(step))
        mc.refresh(suspend=False)

# Move keyframes by value selected
def moveKeys(direction):
    start = None
    end = None
    new_time = None
    try:
        step = getStepTime()
    except:
        step = 1
    if objSelected():
        if keyCount() != None:
            if direction == 'right':
                moveSelectedKeys(step)
            elif direction == 'left':
                moveSelectedKeys('-'+str(step))
        else:
            channels = ml.getSelectedChannels()
            if len(channels) > 0:
                if checkRangeSelected():
                    start, end = getSeletedRange(start,end)
                    for c in channels:
                        keys = getKeysInRange(start,end,channel=c)
                        for k in keys: # frames with keys
                            if direction == 'right':
                                new_time = k + step
                            elif direction == 'left':
                                new_time = k - step
                            if not mc.keyframe(query=True,time=(new_time,),at=c):
                                moveKey(k,new_time,option='over',channel=c)
                            else:
                                displayWarning('Unable to move keys.')
                    mc.currentTime(new_time)
                else:
                    time = getTime()
                    if direction == 'right':
                        new_time = time + step
                    elif direction == 'left':
                        new_time = time - step
                    for c in channels:
                        if not mc.keyframe(query=True,time=(new_time,),at=c):
                            moveKey(time,new_time,option='over',channel=c)
                        else:
                            displayWarning('Unable to move keys.')
                    mc.currentTime(new_time)
            else:
                if checkRangeSelected():
                    start, end = getSeletedRange(start,end)
                    keys = keys = getKeysInRange(start,end)
                    for k in keys: # frames with keys
                        if direction == 'right':
                            new_time = k + step
                        elif direction == 'left':
                            new_time = k - step
                        if not mc.keyframe(query=True,time=(new_time,)):
                            moveKey(k,new_time,option='over')
                        else:
                            displayWarning('Unable to move keys.')
                    mc.currentTime(new_time)
                else:
                    time = getTime()
                    if direction == 'right':
                        new_time = time + step
                    elif direction == 'left':
                        new_time = time - step
                    if not mc.keyframe(query=True,time=(new_time,)):
                        moveKey(time,new_time,option='over')
                    else:
                        displayWarning('Unable to move keys.')
                    mc.currentTime(new_time)
    else:
        displayWarning('Nothing selected.')

# Re-time keys from first key by value selected
def retimeSelectedKeys(*args):
    start = None
    end = None
    new_time = None
    step = getStepTime()
    if keyCount() != None:
        displayWarning('Unable to re-time curves. Please select a channel and re-time on the timeline.')
    else:
        channels = ml.getSelectedChannels()
        if len(channels) != 0:
            if checkRangeSelected():
                start, end = getSeletedRange(start,end)
                for c in channels:
                    keys = getKeysInRange(start,end,channel=c)
                    first_key = keys[0]
                    new_time = first_key
                    # first move keys out of the way
                    temp_keys = []
                    for k in keys:
                        temp_time = k + 1000
                        temp_keys.append(temp_time)
                        moveKey(k,temp_time,option='over',channel=c)
                    # retime keys from first key by value selected
                    new_time = first_key
                    for k in temp_keys:
                        moveKey(k,new_time,option='over',channel=c)
                        new_time += step
                else:
                    displayWarning('No keys on the timeline selected.')
        else:
            if checkRangeSelected():
                start, end = getSeletedRange(start,end)
                keys = getKeysInRange(start,end)
                first_key = keys[0]
                new_time = first_key
                # first move keys out of the way
                temp_keys = []
                for k in keys:
                    temp_time = k + 1000
                    temp_keys.append(temp_time)
                    moveKey(k,temp_time,option='over')
                # retime keys from first key by value selected
                new_time = first_key
                for k in temp_keys:
                    moveKey(k,new_time,option='over')
                    new_time += step
            else:
                displayWarning('No keys on the timeline selected.')
        mc.currentTime(new_time)

def setKeysBy(*args):
    attr = None
    anim_layer = ''
    if objSelected():
        if keyCount() != None:
            keyCurve = mc.keyframe(query=True, name=True)
            for kc in keyCurve:
                keyTimes = mc.keyframe(kc,query=True,selected=True)
                sel, attr = ml.getChannelFromAnimCurve(kc).split('.')
                start = int(keyTimes[0])
                end = int(keyTimes[-1])
                step = getStepTime()
                animlayers =  ml.getSelectedAnimLayers()
                if len(animlayers) > 1:
                    displayWarning('Please select only one anim layer.')
                else:
                    if animlayers:
                        anim_layer = animlayers[0]
                    else:
                        if mc.animLayer('BaseAnimation',query=True,exists=True):
                            anim_layer = 'BaseAnimation'
                        else:
                            anim_layer = ''
                for x in range(start, end, step):
                    if anim_layer == '':
                        mc.setKeyframe(insert=True,t=x,attribute=attr)
                    else:
                        mc.setKeyframe(insert=True,t=x,attribute=attr,animLayer=anim_layer)
        else:
            displayWarning('No keys selected.')

def selectKeysBy(*args):
    attr = None
    step = getStepTime()
    if objSelected():
        if keyCount() != None:
            keyCurve = mc.keyframe(query=True, name=True)
            if len(keyCurve) > 1:
                displayWarning('Please select only one anim curve.')
            else:
                for kc in keyCurve:
                    keyTimes = mc.keyframe(kc,query=True,selected=True)
                    sel, attr = ml.getChannelFromAnimCurve(kc).split('.')
                    start = int(keyTimes[0])
                    end = int(keyTimes[-1])
                    step = getStepTime()
                    mc.selectKey(clear=True)
                    c = 0
                    while c < len(keyTimes):
                    	mc.selectKey(sel, keyframe=True, time=(keyTimes[c], keyTimes[c]), attribute=attr, add=True)
                    	c = c+step
        else:
            displayWarning('No keys selected.')

left_btn_ann = 'Move keys to the left.'
right_btn_ann = 'Move keys to the right.'
retime_btn_ann = 'Re-time Selected Keys by selected value.'
set_btn_ann = 'Set keys between two selected curve keys.'
select_btn_ann = 'Select every number of key from selected keys.'

# tool windows
def tool_win(windowname,title,h,w,buttons = 1,label=[],command=[],annotation=[]):
    if mc.window(windowname, q=True, ex=True):
        mc.deleteUI(windowname)

    mc.window(windowname,title=title, resizeToFitChildren=True,height=h,width=w,menuBar=True)
    mc.menu(label='Help')
    mc.menuItem(label='About', command=about)
    mc.menuItem(label='Documentation', command=(ml._showHelpCommand(website)))
    mc.columnLayout( adjustableColumn=True )
    mc.rowColumnLayout( numberOfRows=1)
    global step
    step = mc.intSliderGrp( label='Step', minValue=1, maxValue=24, value=1, field=True)
    mc.setParent('..')
    for x in range(buttons):
        mc.button(label=label[x], command=eval(command[x]), annotation=annotation[x],width=w)
    mc.setParent('..')
    mc.columnLayout(adj=True)
    mc.helpLine()
    mc.showWindow()

def retimeWin(*args):
    tool_win(windowname='retime_win',title='JNM Re-Time',h=50,w=50,buttons=1,label=['Re-time Selected Keys'],command=['retimeSelectedKeys'],annotation=[retime_btn_ann])

def setselWin(*args):
    tool_win(windowname='setselect_win',title='JNM SetSelect',h=50,w=100,buttons=2,label=['Set Keys','Select Keys'],command=['setKeysBy','selectKeysBy'],annotation=[set_btn_ann,select_btn_ann])

# use ml_utilities.ml.createShelfButton for popup button to create shelf button for the tool
def popUpShelfBtn(parent,shelf_label,shelf_desc,cmds,image='jnm_keys'):
    mc.popupMenu(parent = parent)
    cmd = "import jnm_keyswin;jnm_keyswin." + str(cmds)
    command = "import ml_utilities as ml;ml.createShelfButton(\"{cmd}\",label=\"{shelf_label}\",description=\"{shelf_desc}\",image=\"{image}\")".format(cmd=cmd,shelf_label=shelf_label,shelf_desc=shelf_desc,image=image)

    mc.menuItem(label="Create Shelf Button", command=command, enableCommandRepeat=True)

def about(*args):
    text = 'Author: ' + author + '\n\n' + 'Version: ' + str(version) + '\n\n' + 'Website: ' + website
    mc.confirmDialog(title='About', message=text, button='Close')

# main tool window
def win():
    windowname = "keyswin"
    title = "JNM Keys"
    h = 50
    w = 265
    colw = w/2.75
    # close window if it exists
    if mc.window(windowname, q=True, ex=True):
        mc.deleteUI(windowname)

    window = mc.window(windowname,title=title, resizeToFitChildren=True,height=h,width=w,menuBar=True)

    mc.menu(label='Tools')
    mc.menuItem(label='Add all to shelf', command="import jnm_keyswin;import ml_utilities as ml;" + "ml.createShelfButton(\"{cmd}\",label=\"{shelf_label}\",name=\"{name}\",description=\"{shelf_desc}\",image=\"{image}\")".format(cmd=("import jnm_keyswin;jnm_keyswin.win()"),shelf_label='',name='JNM Keys',shelf_desc=title,image='jnm_keys') + ';' + "ml.createShelfButton(\"{cmd}\",label=\"{shelf_label}\",description=\"{shelf_desc}\",image=\"{image}\")".format(cmd=("import jnm_keyswin;jnm_keyswin.moveKeys(\'left\')"),shelf_label='mvL',shelf_desc='left_btn_ann',image='jnm_keys') + ';' + "ml.createShelfButton(\"{cmd}\",label=\"{shelf_label}\",description=\"{shelf_desc}\",image=\"{image}\")".format(cmd=("import jnm_keyswin;jnm_keyswin.moveKeys(\'right\')"),shelf_label='mvR',shelf_desc='right_btn_ann',image='jnm_keys') + ';' + "ml.createShelfButton(\"{cmd}\",label=\"{shelf_label}\",description=\"{shelf_desc}\",image=\"{image}\")".format(cmd=("import jnm_keyswin;jnm_keyswin.retimeWin()"),shelf_label='reTm',shelf_desc='retime_btn_ann',image='jnm_retime') + ';' + "ml.createShelfButton(\"{cmd}\",label=\"{shelf_label}\",description=\"{shelf_desc}\",image=\"{image}\")".format(cmd=("import jnm_keyswin;jnm_keyswin.setselWin()"),shelf_label='setsel',shelf_desc='set_btn_ann',image='jnm_setkeys'))

    mc.menu(label='Help')
    mc.menuItem(label='About', command=about)
    mc.menuItem(label='Documentation', command=(ml._showHelpCommand(website)))

    mc.columnLayout(adj=True)
    global step
    step = mc.intSliderGrp( label='Step', minValue=1, maxValue=24, value=1, field=True)
    mc.setParent('..')
    mc.rowColumnLayout( numberOfRows=1)
    left_btn = mc.button(label='<<< Move Left', command=('import jnm_keyswin;jnm_keyswin.moveKeys(\'left\')'), annotation=left_btn_ann,width=w)
    popUpShelfBtn(left_btn,'mvL',left_btn_ann,'moveKeys(\'left\')')
    right_btn = mc.button(label='Move Right >>>', command=('import jnm_keyswin;jnm_keyswin.moveKeys(\'right\')'), annotation=right_btn_ann,width=w)
    popUpShelfBtn(right_btn,'mvR',right_btn_ann,'moveKeys(\'right\')')
    mc.setParent('..')
    mc.columnLayout(adj=True)
    retime_btn = mc.button(label='Re-time Selected Keys', command='import jnm_keyswin;jnm_keyswin.retimeSelectedKeys()', annotation=retime_btn_ann,width=w*2)
    popUpShelfBtn(retime_btn,'reTm', retime_btn_ann,'retimeWin()',image='jnm_retime')
    mc.setParent('..')
    mc.rowColumnLayout( numberOfRows=1)
    set_btn = mc.button(label='Set Keys', command='import jnm_keyswin;jnm_keyswin.setKeysBy()', annotation=set_btn_ann,width=w)
    popUpShelfBtn(set_btn,'setsel', set_btn_ann,cmds='setselWin()',image='jnm_setkeys')
    select_btn = mc.button(label='Select Keys', command='import jnm_keyswin;jnm_keyswin.selectKeysBy()', annotation=select_btn_ann,width=w)
    popUpShelfBtn(select_btn,'setsel', set_btn_ann,cmds='setselWin()',image='jnm_setkeys')
    mc.setParent('..')
    mc.columnLayout(adj=True)
    mc.helpLine()
    mc.showWindow( window )
