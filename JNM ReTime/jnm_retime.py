"""
author: Jose N. Molina

website: jnmolina.com

description:

    Re-time:        Based on the first selected key on the timeline, the range of selected keys are re-timed by the number selected in the UI.
                    If any channels are selected, it only re-times the key(s) on those channels.

                    import jnm_retime;jnm_retime.win()

"""
import maya.cmds as mc
import maya.mel as mm
from maya import OpenMaya
author = 'Jose N. Molina'
version = 1
website = 'jnmolina.com'

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

# JNM scripts

def displayWarning(text):
    return OpenMaya.MGlobal.displayWarning(text)

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

# Re-time keys from first key by value selected

def retimeSelectedKeys(*args):
    start = None
    end = None
    new_time = None
    step = getStepTime()
    if keyCount() != None:
        displayWarning(
            'Unable to re-time curves. Please select a channel and re-time on the timeline.')
    else:
        channels = getSelectedChannels()
        if len(channels) != 0:
            if checkRangeSelected():
                start, end = getSeletedRange(start, end)
                for c in channels:
                    keys = getKeysInRange(start, end, channel=c)
                    first_key = keys[0]
                    new_time = first_key
                    # first move keys out of the way
                    temp_keys = []
                    for k in keys:
                        temp_time = k + 1000
                        temp_keys.append(temp_time)
                        moveKey(k, temp_time, option='over', channel=c)
                    # retime keys from first key by value selected
                    new_time = first_key
                    for k in temp_keys:
                        moveKey(k, new_time, option='over', channel=c)
                        new_time += step
            else:
                displayWarning('No keys on the timeline selected.')
        else:
            if checkRangeSelected():
                start, end = getSeletedRange(start, end)
                keys = getKeysInRange(start, end)
                first_key = keys[0]
                new_time = first_key
                # first move keys out of the way
                temp_keys = []
                for k in keys:
                    temp_time = k + 1000
                    temp_keys.append(temp_time)
                    moveKey(k, temp_time, option='over')
                # retime keys from first key by value selected
                new_time = first_key
                for k in temp_keys:
                    moveKey(k, new_time, option='over')
                    new_time += step
            else:
                displayWarning('No keys on the timeline selected.')
        if (new_time == None):
            pass
        else:
            mc.currentTime(new_time)

w = 50

def about(*args):
    text = 'Author: ' + author + '\n\n' + 'Version: ' + \
        str(version) + '\n\n' + 'Website: ' + website
    mc.confirmDialog(title='About', message=text, button='Close')

retime_btn_ann = 'Re-time Selected Keys by selected value.'

def win(*args):
    if mc.window('retime_win', q=True, ex=True):
        mc.deleteUI('retime_win')

    mc.window('retime_win', title='JNM Re-Time',
              resizeToFitChildren=True, height=50, width=w, menuBar=True)
    mc.menu(label='Help')
    mc.menuItem(label='About', command=about)
    mc.menuItem(label='Website', command=(
        'import maya.cmds as mc;mc.showHelp("http://www.'+website+'",absolute=True)'))
    mc.columnLayout(adjustableColumn=True)
    mc.rowColumnLayout(adj=True, numberOfRows=2)
    global step
    step = mc.intSliderGrp(label='Step', minValue=1,
                           maxValue=24, value=1, field=True)
    mc.button(label='Re-time Selected Keys',
              command=retimeSelectedKeys, annotation=retime_btn_ann, w=w)
    mc.setParent('..')
    mc.columnLayout(adj=True)
    mc.helpLine()
    mc.showWindow()
