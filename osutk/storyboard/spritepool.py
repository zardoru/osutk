from . import TemporalSprite

class SpritePool(object):

    def __init__(self, sprites, active_criteria=lambda obj, x: True):
        self.sprites = sprites
        self.active_criteria = active_criteria

    def get_free(self, *criteria_params):
        for x in self.sprites:
            if self.active_criteria(x, *criteria_params):
                return x
               
        return None

def is_tempsprite_active(obj, t_start, t_end):
    return obj.is_active_at(t_start, t_end)

class TemporalSpritePool(SpritePool):
    # if auto_add_periods is true, then all free sprites returned will now include
    # the requested active period into the temporalsprite.
    def __init__(self, sprites, auto_add_periods=True):
        assert(all([x is TemporalSprite for x in sprites]), "Input is not TemporalSprite")
        super().__init__(sprites, is_tempsprite_active)
        self.auto_add_periods = auto_add_periods


    def get_free(self, t_start, t_end):
        assert(t_start < t_end)

        item = super().get_free(t_start, t_end)
        if item and self.auto_add_periods:
            item.add_active_period((t_start, t_end))

        return item

    # activate and deactivate fade of objects automatically
    def auto_fade_objects(self):
        for x in self.sprites:
            for segment in x.active_periods:
                x.fade(_st=segment[0], _et=segment[1], _sv=1)
                x.fade(_st=segment[1], _sv=0)