"""
author: Jose N. Molina

website: jnmolina.com

description:

    Shelf Button: Create motion trail for selected objects for playback range or selected range.
        Right-click:
            Options: Opens Maya Options window.
            Cleanup Last: Remove last created motion trail.
            Cleanup All: Remove all motion trails in the scene.

        Doulbe Click - UI: Fade frames and Show Keyframe Number options.
            Attributes: Selects motion trails and toggles Attribute Editor to show all options.

    import jnm_motrails;jnm_motrails.win()

"""
import maya.cmds as mc
import maya.mel as mm
from maya import OpenMaya
author = 'Jose N. Molina'
version = 1
website = 'jnmolina.com'

def displayWarning(text):
    return OpenMaya.MGlobal.displayWarning(text)

def objSelected(*args):
    sel = mc.ls(sl=True)
    if sel:
        return sel
    else:
        displayWarning('Nothing selected.')

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

def checkRangeSelected(*args):
    if mc.timeControl(gPlayBackSlider, query=True, rangeVisible=True):
        return True
    else:
        return False

# Motion Trails
def setMoTrails(*args):
    sel = objSelected()
    if objSelected():
        set_global()
        start = None
        end = None
        inc = 1
        if checkRangeSelected():
            start, end = getSeletedRange(start, end)
        else:
            start, end = getpbRange(start, end)
        # create motion trails, save for cleanup
        m = mc.snapshot(sel, motionTrail=True, increment=inc,
                        startTime=start, endTime=end)
        global jnm_mts
        jnm_mts.append(m)
        # check if ui is open to query checkboxes
        if mc.window('jnm_motrails_win', q=True, ex=True):
            global show_keynums_box
            if mc.checkBox(show_keynums_box, query=True, value=True) == 1:
                showKeyframeNumbers()
            global fade_frames_box
            if mc.checkBox(fade_frames_box, query=True, value=True) == 1:
                fadeFrames()
    else:
        displayWarning('Nothing selected.')

def clearLastMoTrails(*args):
    for m in get_global():
        mc.delete(m)
    set_global()

def clearAllMoTrails(*args):
    for each in mc.ls(type='motionTrail'):
        mc.delete(each)

def set_global(*args):
    global jnm_mts
    jnm_mts = []

def get_global(*args):
    global jnm_mts
    return jnm_mts

def showAttributes(*args):
    mts = get_global()
    handles = [x[i] for x in mts for i in range(0, len(x), 2)]
    mc.select(handles)
    mm.eval('ToggleAttributeEditor')

def showKeyframeNumbers(*args):
    mts = get_global()
    handles = [x[i] for x in mts for i in range(0, len(x), 2)]
    for handle in handles:
        mc.setAttr(handle + '.showFrames', 1)

def fadeFrames(*args):
    mts = get_global()
    handles = [x[i] for x in mts for i in range(0, len(x), 2)]
    for handle in handles:
        mc.setAttr(handle + '.fadeInoutFrames', 10)
        mc.setAttr(handle + '.preFrame', 10)
        mc.setAttr(handle + '.postFrame', 10)

def about(*args):
    text = 'Author: ' + author + '\n\n' + 'Version: ' + \
        str(version) + '\n\n' + 'Website: ' + website
    mc.confirmDialog(title='About', message=text, button='Close')

motrails_anno = 'Create Motion Trail for selected on selected range or playback range.'
cleanupLastMoTrails_anno = 'Remove last created motion trail(s).'
cleanupAllMoTrails_anno = 'Remove all motion trail(s).'
showAttributes_anno = 'Selects motrail(s), toggles Attribute Editor.'
fadeFrames_anno = 'Fade frames of the motion trails whencreated.'
show_keynums_anno = 'Show keyframe numbers for the motion trails.'

w = 300

def win(*args):
    if mc.window('jnm_motrails_win', q=True, ex=True):
        mc.deleteUI('jnm_motrails_win')

    mc.window('jnm_motrails_win', title='JNM MoTrails',
              resizeToFitChildren=True, height=50, width=w, menuBar=True)
    mc.menu(label='Help')
    mc.menuItem(label='About', command=about)
    mc.menuItem(label='Website', command=(
        'import maya.cmds as mc;mc.showHelp("http://www.'+website+'",absolute=True)'))
    mc.columnLayout(adjustableColumn=True)
    mc.rowColumnLayout(adj=True, numberOfRows=4)
    mc.button(label='MoTrails', command=setMoTrails,
              annotation=motrails_anno, w=w)
    mc.button(label='Cleanup Last', command=clearLastMoTrails,
              annotation=cleanupLastMoTrails_anno, w=w)
    mc.button(label='Cleanup All', command=clearAllMoTrails,
              annotation=cleanupAllMoTrails_anno, w=w)
    mc.button(label='Attributes', command=showAttributes,
              annotation=showAttributes_anno, w=w)
    mc.setParent('..')
    mc.columnLayout(adjustableColumn=True)
    mc.separator(style='single', horizontal=True, h=10)
    global show_keynums_box
    show_keynums_box = mc.checkBox(
        label='Show Keyframe Numbers', annotation=show_keynums_anno)
    global fade_frames_box
    fade_frames_box = mc.checkBox(
        label='Fade frames', annotation=fadeFrames_anno)
    mc.setParent('..')
    mc.columnLayout(adjustableColumn=True)
    mc.helpLine()
    mc.showWindow()
