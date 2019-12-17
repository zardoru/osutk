__author__ = 'Agka'


class Ease(object):
    """
    Ease constants. For reference.
    """
    Linear = 0
    Out = 1
    In = 2
    QuadIn = 3
    QuadOut = 4
    QuadInOut = 5
    CubicIn = 6
    CubicOut = 7
    CubicInOut = 8
    QuartIn = 9
    QuartOut = 10
    QuartInOut = 11
    QuintIn = 12
    QuintOut = 13
    QuintInOut = 14
    SineIn = 15
    SineOut = 16
    SineInOut = 17
    ExpoIn = 18
    ExpoOut = 19
    ExpoInOut = 20
    CircIn = 21
    CircOut = 22
    CircInOut = 23
    ElasticIn = 24
    ElasticOut = 25
    ElasticHalfOut = 26
    ElasticQuarterOut = 27
    ElasticInOut = 28
    BackIn = 29
    BackOut = 30
    BounceIn = 32
    BounceOut = 33
    BounceInOut = 34


class Command(object):
    """
    Command types. For internal use.
    """
    Fade = 1
    Move = 2
    MoveX = 3
    MoveY = 4
    Scale = 5
    VectorScale = 6
    Rotate = 7

    # colorization
    Color = 8
    Colour = 8

    # parameters
    FlipHorizontally = 9
    FlipVertically = 10
    MakeAdditive = 11

    CommandTypes = {
        Fade,
        Move,
        MoveX,
        MoveY,
        Scale,
        VectorScale,
        Rotate,
        Color,
        FlipHorizontally,
        FlipVertically,
        MakeAdditive
    }

    Shorthand = {
        Fade: 'F',
        MoveX: 'MX',
        MoveY: 'MY',
        Scale:  'S',
        Rotate: 'R',
        VectorScale: 'V',
        Move: 'M',
        Color: 'C',
        FlipHorizontally: 'P',
        FlipVertically: 'P',
        MakeAdditive: 'P'
    }

    @staticmethod
    def is_reducible(evt_type):
        return evt_type < Command.FlipHorizontally


class Origin(object):
    """
    Origin types. For brevity.
    """
    TopLeft = 'TopLeft'
    TL = TopLeft
    TopCentre = 'TopCentre'
    TopCenter = 'TopCentre'
    TC = TopCenter
    TopRight = 'TopRight'
    TR = TopRight
    CentreLeft = 'CentreLeft'
    CenterLeft = 'CentreLeft'
    CL = CenterLeft
    Center = 'Centre'
    Centre = 'Centre'
    CC = Center
    CentreRight = "CentreRight"
    CenterRight = "CentreRight"
    CR = "CentreRight"
    BottomLeft = 'BottomLeft'
    BL = BottomLeft
    BottomCentre = 'BottomCentre'
    BottomCenter = 'BottomCentre'
    BC = BottomCenter
    BottomRight = 'BottomRight'
    BR = BottomRight


class Layer(object):
    """
    Layer types. For brevity.
    """
    Background = 'Background'
    Fail = 'Fail'
    Pass = 'Pass'
    Foreground = 'Foreground'


class Screen(object):
    """
    Screen sizes and reference points.
    """
    Width = 640
    WidthWidescreen = 853
    Height = 480

    HalfWidth = 320
    HalfHeight = 240

    StartWidescreen = -106
    EndWidescreen = 746

    @staticmethod
    def is_point_inside(point, widescreen=False):
        x, y = point[0], point[1]
        if widescreen:
            return Screen.StartWidescreen <= x <= Screen.EndWidescreen and \
                   0 <= y <= Screen.Height
        else:
            return 0 <= x <= Screen.Width and \
                   0 <= y <= Screen.Height
