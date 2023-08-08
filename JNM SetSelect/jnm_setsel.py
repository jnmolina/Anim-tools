"""
author: Jose N. Molina

website: jnmolina.com

description:

    Set/Select:     Sets/Select keys every number of frames between two selected keyframes. Number taken from UI selected value.
                    If any animation layers exist, you must also select the curves animation layer.

                    import jnm_setselect;jnm_setselect.win()

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

# JNM scripts

def displayWarning(text):
    return OpenMaya.MGlobal.displayWarning(text)

def objSelected(*args):
    sel = mc.ls(sl=True)
    if sel:
        return sel
    else:
        displayWarning('Nothing selected.')

def getStepTime(*args):
    global step
    return mc.intSliderGrp(step, query=True, value=True)

# get curve keyframes selected
def keyCount(*args):
    count = mc.keyframe(query=True, timeChange=True, selected=True)
    return count

def setKeysBy(*args):
    attr = None
    anim_layer = ''
    if objSelected():
        if keyCount() != None:
            keyCurve = mc.keyframe(query=True, name=True)
            for kc in keyCurve:
                keyTimes = mc.keyframe(kc, query=True, selected=True)
                sel, attr = getChannelFromAnimCurve(kc).split('.')
                start = int(keyTimes[0])
                end = int(keyTimes[-1])
                step = getStepTime()
                animlayers = getSelectedAnimLayers()
                if len(animlayers) > 1:
                    displayWarning('Please select only one anim layer.')
                else:
                    if animlayers:
                        anim_layer = animlayers[0]
                    else:
                        if mc.animLayer('BaseAnimation', query=True, exists=True):
                            anim_layer = 'BaseAnimation'
                        else:
                            anim_layer = ''
                for x in range(start, end, step):
                    if anim_layer == '':
                        mc.setKeyframe(insert=True, t=x, attribute=attr)
                    else:
                        mc.setKeyframe(insert=True, t=x,
                                       attribute=attr, animLayer=anim_layer)
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
                    keyTimes = mc.keyframe(kc, query=True, selected=True)
                    sel, attr = getChannelFromAnimCurve(kc).split('.')
                    start = int(keyTimes[0])
                    end = int(keyTimes[-1])
                    step = getStepTime()
                    mc.selectKey(clear=True)
                    c = 0
                    while c < len(keyTimes):
                        mc.selectKey(sel, keyframe=True, time=(
                            keyTimes[c], keyTimes[c]), attribute=attr, add=True)
                        c = c+step
        else:
            displayWarning('No keys selected.')

def about(*args):
    text = 'Author: ' + author + '\n\n' + 'Version: ' + \
        str(version) + '\n\n' + 'Website: ' + website
    mc.confirmDialog(title='About', message=text, button='Close')

set_btn_ann = 'Set keys between two selected curve keys.'
select_btn_ann = 'Select every number of key from selected keys.'

w = 50

def win(*args):
    if mc.window('setselect_win', q=True, ex=True):
        mc.deleteUI('setselect_win')

    mc.window('setselect_win', title='JNM SetSelect',
              resizeToFitChildren=True, height=50, width=w, menuBar=True)
    mc.menu(label='Help')
    mc.menuItem(label='About', command=about)
    mc.menuItem(label='Website', command=(
        'import maya.cmds as mc;mc.showHelp("http://www.'+website+'",absolute=True)'))
    mc.columnLayout(adjustableColumn=True)
    mc.rowColumnLayout(adj=True, numberOfRows=3)
    global step
    step = mc.intSliderGrp(label='Step', minValue=1,
                           maxValue=24, value=1, field=True)
    mc.button(label='Set Keys', command=setKeysBy, annotation=set_btn_ann, w=w)
    mc.button(label='Select Keys', command=selectKeysBy,
              annotation=select_btn_ann, w=w)
    mc.setParent('..')
    mc.columnLayout(adjustableColumn=True)
    mc.helpLine()
    mc.showWindow()
