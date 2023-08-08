"""
author: Jose N. Molina

website: jnmolina.com

description:

    Moves the current keyframe or selected keyframes (on the timeline or in the Graph Editor).
    If any channels are selected, it only moves the key(s) on those channels.
    If no keyframe at the current time, it moves an existing keyframe to the spot
        -   Left: move the next key back to the current time
        -   Right: move the previous key forward to current time

    Can be set as hotkeys:
    import jnm_movekeys;jnm_movekeys.moveKeys('left')
    import jnm_movekeys;jnm_movekeys.moveKeys('right')

    If the tool window is open, it takes the value from the slider, otherwise it defaults to 1.


"""
from maya import OpenMaya
import maya.mel as mm
import maya.cmds as mc
author = 'Jose N. Molina'
version = 1
website = 'jnmolina.com'
tool = 'jnm_movekeys'


# from Morgan Loomis' ml_utilities http://morganloomis.com/tool/ml_utilities/
# -= ml_utilities.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Revision 34
#   / / / / / / /  2019-03-07
#  /_/ /_/ /_/_/  _________
#               /_________/
#
#     ______________
# - -/__ License __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Copyright 2018 Morgan Loomis
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

def getSelectedChannels():
    '''
    Return channels that are selected in the channelbox
    '''

    if not mc.ls(sl=True):
        return
    gChannelBoxName = mm.eval('$temp=$gChannelBoxName')
    sma = mc.channelBox(gChannelBoxName, query=True, sma=True)
    ssa = mc.channelBox(gChannelBoxName, query=True, ssa=True)
    sha = mc.channelBox(gChannelBoxName, query=True, sha=True)

    channels = list()
    if sma:
        channels.extend(sma)
    if ssa:
        channels.extend(ssa)
    if sha:
        channels.extend(sha)

    return channels


def getChannelFromAnimCurve(curve, plugs=True):
    '''
    Finding the channel associated with a curve has gotten really complicated since animation layers.
    This is a recursive function which walks connections from a curve until an animated channel is found.
    '''

    # we need to save the attribute for later.
    attr = ''
    if '.' in curve:
        curve, attr = curve.split('.')

    nodeType = mc.nodeType(curve)
    if nodeType.startswith('animCurveT') or nodeType.startswith('animBlendNode'):
        source = mc.listConnections(curve+'.output', source=False, plugs=plugs)
        if not source and nodeType == 'animBlendNodeAdditiveRotation':
            # if we haven't found a connection from .output, then it may be a node that uses outputX, outputY, etc.
            # get the proper attribute by using the last letter of the input attribute, which should be X, Y, etc.
            # if we're not returning plugs, then we wont have an attr suffix to use, so just use X.
            attrSuffix = 'X'
            if plugs:
                attrSuffix = attr[-1]

            source = mc.listConnections(
                curve+'.output'+attrSuffix, source=False, plugs=plugs)
        if source:
            nodeType = mc.nodeType(source[0])
            if nodeType.startswith('animCurveT') or nodeType.startswith('animBlendNode'):
                return getChannelFromAnimCurve(source[0], plugs=plugs)
            return source[0]


def getSelectedAnimLayers():
    '''
    Return the names of the layers which are selected
    '''
    layers = list()
    for each in mc.ls(type='animLayer'):
        if mc.animLayer(each, query=True, selected=True):
            layers.append(each)
    return layers


MAYA_VERSION = mm.eval('getApplicationVersionAsFloat')

def createShelfButton(command, label='', name=None, description='', image=None, labelColor=(1, 0.5, 0), labelBackgroundColor=(0, 0, 0, 0.5), backgroundColor=None):
    '''
    Create a shelf button for the command on the current shelf
    '''
    # some good default icons:
    # menuIconConstraints - !
    #render_useBackground - circle
    # render_volumeShader - black dot
    #menuIconShow - eye

    gShelfTopLevel = mm.eval('$temp=$gShelfTopLevel')
    if not mc.tabLayout(gShelfTopLevel, exists=True):
        OpenMaya.MGlobal.displayWarning('Shelf not visible.')
        return

    if not name:
        name = label

    if not image:
        image = getIcon(name)
    if not image:
        image = 'render_useBackground'

    shelfTab = mc.shelfTabLayout(gShelfTopLevel, query=True, selectTab=True)
    shelfTab = gShelfTopLevel+'|'+shelfTab

    # add additional args depending on what version of maya we're in
    kwargs = {}
    if MAYA_VERSION >= 2009:
        kwargs['commandRepeatable'] = True
    if MAYA_VERSION >= 2011:
        kwargs['overlayLabelColor'] = labelColor
        kwargs['overlayLabelBackColor'] = labelBackgroundColor
        if backgroundColor:
            kwargs['enableBackground'] = bool(backgroundColor)
            kwargs['backgroundColor'] = backgroundColor

    return mc.shelfButton(parent=shelfTab, label=name, command=command, imageOverlayLabel=label, image=image, annotation=description, width=32, height=32, align='center', **kwargs)

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
    return mc.intSliderGrp(step, query=True, value=True)

gPlayBackSlider = mm.eval('$temp=$gPlayBackSlider')

# get the selected range

def getSeletedRange(start, end):
    pbRange = mc.timeControl(gPlayBackSlider, query=True, rangeArray=True)
    start = float(pbRange[0])
    end = float(pbRange[1])
    return start, end

# get the timeslider min/max

def getpbRange(start, end):
    start = mc.playbackOptions(query=True, min=True)
    end = mc.playbackOptions(query=True, max=True)
    return start, end

# check if a curve key is selected

def checkKeysSelected(*args):
    keyCount = mc.keyframe(query=True, keyframeCount=True)
    if keyCount:
        pass
    else:
        displayWarning('No keys in selected range.')

# check if a key exists for the given frame

def keyExists(t, channel=None):
    if channel != None:
        if mc.keyframe(query=True, time=(t,), at=channel) == None:
            return False
        else:
            return True
    else:
        if mc.keyframe(query=True, time=(t,)) == None:
            return False
        else:
            return True

# get frames that have keyframes

def getKeysInRange(start, end, channel=None):
    keys = []
    mc.refresh(suspend=True)
    for x in range(int(start), int(end)):
        if channel != None:
            if keyExists(x, channel):
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

def moveKey(time, new_time, option, channel=None):
    mc.refresh(suspend=True)
    if channel != None:
        mc.keyframe(edit=True, time=(time,), option=option,
                    timeChange=int(new_time), at=channel)
    else:
        mc.keyframe(edit=True, time=(time,), option=option,
                    timeChange=int(new_time))
    mc.refresh(suspend=False)

# Move selected keys in Graph Editor

def moveSelectedKeys(step):
    mc.refresh(suspend=True)
    mc.keyframe(edit=True, animation='keysOrObjects',
                option='move', relative=True, timeChange=int(step))
    mc.refresh(suspend=False)

def keyMove(t, direction, *args):
    channels = getSelectedChannels()
    if len(channels) > 0:
        for c in channels:
            mc.selectKey(at=c)
            next = mc.findKeyframe(time=(t,), which='next')
            prev = mc.findKeyframe(time=(t,), which='previous')
            mc.selectKey(clear=True)
            if direction == 'right':
                mc.selectKey(at=c,time=(prev,prev))
                step = t - prev
                moveSelectedKeys(step)
                mc.selectKey(clear=True)
            elif direction == 'left':
                mc.selectKey(at=c,time=(next,next))
                step = next - t
                moveSelectedKeys(-step)
                mc.selectKey(clear=True)
    else:
        next = mc.findKeyframe(time=(t,), which='next')
        prev = mc.findKeyframe(time=(t,), which='previous')
        if direction == 'right':
            moveKey(prev,t,'over')
        elif direction == 'left':
            moveKey(next,t,'over')

# Move keyframes by value selected
# order: curve keys, prev/next key moves, current key moves
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
            t = mc.currentTime(query=True)
            currentKey = keyExists(t)
            if not currentKey:
                keyMove(t,direction)
            else:
                channels = getSelectedChannels()
                if len(channels) > 0:
                    if checkRangeSelected():
                        start, end = getSeletedRange(start, end)
                        for c in channels:
                            keys = getKeysInRange(start, end, channel=c)
                            for k in keys:  # frames with keys
                                if direction == 'right':
                                    new_time = k + step
                                elif direction == 'left':
                                    new_time = k - step
                                if not mc.keyframe(query=True, time=(new_time,), at=c):
                                    moveKey(k, new_time, option='over', channel=c)
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
                            if not mc.keyframe(query=True, time=(new_time,), at=c):
                                moveKey(time, new_time, option='over', channel=c)
                            else:
                                displayWarning('Unable to move keys.')
                        mc.currentTime(new_time)
                else:
                    if checkRangeSelected():
                        start, end = getSeletedRange(start, end)
                        keys = keys = getKeysInRange(start, end)
                        for k in keys:  # frames with keys
                            if direction == 'right':
                                new_time = k + step
                            elif direction == 'left':
                                new_time = k - step
                            if not mc.keyframe(query=True, time=(new_time,)):
                                moveKey(k, new_time, option='over')
                            else:
                                displayWarning('Unable to move keys.')
                        mc.currentTime(new_time)
                    else:
                        time = getTime()
                        if direction == 'right':
                            new_time = time + step
                        elif direction == 'left':
                            new_time = time - step
                        if not mc.keyframe(query=True, time=(new_time,)):
                            moveKey(time, new_time, option='over')
                        else:
                            displayWarning('Unable to move keys.')
                        mc.currentTime(new_time)
    else:
        displayWarning('Nothing selected.')

left_btn_ann = 'Move keys to the left.'
right_btn_ann = 'Move keys to the right.'

def about(*args):
    text = 'Author: ' + author + '\n\n' + 'Version: ' + \
        str(version) + '\n\n' + 'Website: ' + website
    mc.confirmDialog(title='About', message=text, button='Close')

# use ml_utilities.createShelfButton for popup button to create shelf button for the tool

def popUpShelfBtn(parent, shelf_label, shelf_desc, cmds, image=tool):
    mc.popupMenu(parent=parent)
    cmd = "import " + tool + ";" + tool + "." + str(cmds)
    command = "import {tool};{tool}.createShelfButton(\"{cmd}\",label=\"{shelf_label}\",description=\"{shelf_desc}\",image=\"{image}\")".format(tool=tool,
                                                                                                                                                cmd=cmd, shelf_label=shelf_label, shelf_desc=shelf_desc, image=image)
    mc.menuItem(label="Create Shelf Button",
                command=command, enableCommandRepeat=True)
# main tool window

def win():
    windowname = "movekeyswin"
    title = "JNM MoveKeys"
    h = 50
    w = 200
    colw = w/2.75
    # close window if it exists
    if mc.window(windowname, q=True, ex=True):
        mc.deleteUI(windowname)

    window = mc.window(windowname, title=title,
                       resizeToFitChildren=True, height=h, width=w, menuBar=True)

    mc.menu(label='Help')
    mc.menuItem(label='About', command=about)
    mc.menuItem(label='Website', command=(
        'import maya.cmds as mc;mc.showHelp("http://www.'+website+'",absolute=True)'))

    mc.columnLayout(adj=True)
    global step
    step = mc.intSliderGrp(label='Step', minValue=1, maxValue=24, value=1, field=True)
    mc.setParent('..')
    mc.rowColumnLayout(numberOfRows=1)
    left_btn = mc.button(label='<<< Move Left', command=(
        'import jnm_movekeys;jnm_movekeys.moveKeys(\'left\')'), annotation=left_btn_ann, width=w)
    popUpShelfBtn(left_btn, 'mvL', left_btn_ann, 'moveKeys(\'left\')')
    right_btn = mc.button(label='Move Right >>>', command=(
        'import jnm_movekeys;jnm_movekeys.moveKeys(\'right\')'), annotation=right_btn_ann, width=w)
    popUpShelfBtn(right_btn, 'mvR', right_btn_ann, 'moveKeys(\'right\')')
    mc.setParent('..')
    mc.columnLayout(adj=True)
    mc.helpLine()
    mc.showWindow(window)
