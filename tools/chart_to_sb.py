from bisect import bisect
from itertools import accumulate
from osutk.storyboard.spritepool import TemporalSpritePool
from osutk.storyboard import TemporalSprite, Sprite, Layer, Origin, Screen
from numpy import arange

# calculates a good constant for making a beat a specific number of px.
# works with ScrollCtx below
def px_per_beat(px_for_beat, basebpm, second_factor=1000):
    bps = basebpm / (60 * second_factor)
    return px_for_beat * bps

class ScrollCtx(object):
    def _generate_accom_scroll(self, sv):
        if len(sv) > 0:
            ret = [(sv[0][0], 0)]
        else:
            ret = [(0, 0)]

        for i, (t, _) in enumerate(sv[1:]):
            # add integral from previous time to current time
            integral = (t - ret[i][0]) * sv[i][1] + ret[i][1]
            ret.append((t, integral))

        return ret

    # px_per_unit is a factor that converts bpm-ms or bpm-s or sv-ms or sv-s 
    # into a pixel unit. 
    def __init__(self, sv, speed=lambda x: 1):
        # an array of (time, sv)
        self.sv = list(sorted(sv, key=lambda x: x[0])) 

        # an array of (time, integral of sv at time)
        self.accom_scroll = self._generate_accom_scroll(self.sv) 
        self.accom_scroll_time = [x[0] for x in self.accom_scroll]

        # a function that returns the speed multiplier
        self.spd = speed

    def get_displacement_at_time(self, t):
        # find the index of current time t
        index = bisect(self.accom_scroll_time, t)
        if index > 0: index -= 1
        return self.accom_scroll[index][1] + self.sv[index][1] * (t - self.accom_scroll_time[index])

    # Get the position of an object given a current time
    def get_object_position_at_time(self, t, t_obj):
        pos = self.get_displacement_at_time(t)
        pos_obj = self.get_displacement_at_time(t_obj)
        speed_mul = self.spd(t)
        # change the relative position by the speed multiplier
        return (pos_obj - pos) * speed_mul



# no long note support for now, maybe ever
class Gear(object):
    def __init__(self, 
        x_start,
        lane_images, 
        lane_widths,
        note_images, 
        note_image_width, # actual image size
        bg_image,
        bg_size,
        judgeline_image,
        y_judgeline):
        self.x_start = x_start
        self.lane_images = lane_images
        self.lane_widths = lane_widths
        self.note_images = note_images
        self.note_image_width = note_image_width
        self.bg_image = bg_image
        self.bg_size = bg_size
        self.y_judgeline = y_judgeline
        self.judgeline_image = judgeline_image

        self.gear_width = self.calculate_gear_width()
        self.lane_pos = list(accumulate([self.x_start, *self.lane_widths]))[:-1]

    @property
    def lane_count(self):
        return len(self.lane_pos)

    def calculate_gear_width(self):
        return sum(self.lane_widths)

    def generate_background(self, dst_size=None):
        if dst_size is None:
            dst_size = (self.gear_width, 640)

        if self.bg_image is None:
            return
        
        if any(x == 0 for x in self.bg_size):
            print("Size is zero, not generating a gear background")
            return

        x_scale = dst_size[0] / self.bg_size[0]
        y_scale = dst_size[1] / self.bg_size[1]

        spr = Sprite(file=self.bg_image,
                     location=(self.x_start, 0))
        
        # make it appear, and make it the right size
        spr.fade()
        spr.vector_scale(_sx=x_scale, _sy=y_scale)
        return spr


    # todo: arbitrary direction, given by unit 2d vector
    def generate_note(self, lane):
        spr = TemporalSprite(layer=Layer.Foreground,
                             origin=Origin.CentreLeft,
                             location=(self.lane_pos[lane], -100),
                             file=self.note_images[lane])

        spr.vector_scale(_sx = self.lane_widths[lane] / self.note_image_width)

        return spr
    
    def generate_judgeline(self, dst_width):
        spr = Sprite(origin=Origin.CentreLeft,
                     file=self.judgeline_image,
                     location=(self.x_start, self.y_judgeline))

        return spr

    def generate_gear(self):
        self.generate_background()
        self.generate_judgeline(self.gear_width)


class StoryboardMap(object):
    def __init__(self, 
    gear,
    chart, 
    framerate,
    base_bpm,
    beat_height,
    speed_func=lambda x: 1):
        self.gear = gear
        self.chart = chart
        self.framerate = framerate 

        self.base_bpm = base_bpm
        self.px_per_beat = px_per_beat(beat_height, base_bpm)

        # + 3 seconds
        self.song_duration = chart.get_last_object_time() + 3000

        # Lane object pools
        self.pools = [TemporalSpritePool([]) for x in range(chart.lane_count)]

        self.scroll_ctx = ScrollCtx(
            self.get_sv_time_pairs(chart), 
            speed_func
        )

    def get_sv_time_pairs(self, chart):
        ret = []
        for x in chart.timing_points:
            if x.uninherited == 1:
                ratio = x.bpm / self.base_bpm
                ret.append((x.time, ratio))
            else:
                ret.append((x.time, x.sv))
        return ret

    # we could make paths by getting fancy here
    def scroll_to_screen_pos(self, lane, pos):
        return (self.gear.lane_pos[lane], pos * self.px_per_beat + self.gear.y_judgeline)

    # ah, alas, it'd be simple if it was only scrolls, but 
    # no guarantees about speeds and whatnot make this really expensive.
    def get_visible_time_segments(self, lane, t_obj):
        time_interval = 1000 / self.framerate
        segments = []
        start_vis = None
        for vis_test_time in arange(0, self.song_duration, time_interval):
            pos = self.scroll_ctx.get_object_position_at_time(vis_test_time, t_obj)
            screen_pos = self.scroll_to_screen_pos(lane, pos)
            
            #if pos > -10000:
            #    print(pos, screen_pos, vis_test_time)

            point_test_is_inside = Screen.is_point_inside(screen_pos, widescreen=True)

            if point_test_is_inside:
                # check if we are going to begin  a visibility segment
                # print("VISIBLE")
                if start_vis is None:
                    #print("start segment at {}      ".format(vis_test_time))
                    start_vis = vis_test_time
                else:
                    pass # we're still in the visible segment checking
            else: # not visible
                # print("NOT VISIBLE")
                # was it visible before?
                if start_vis is not None:
                    # close the segment
                    #print("close segment at {}".format(vis_test_time))
                    segments.append((start_vis, vis_test_time))
                    start_vis = None
                else:
                    pass # wasn't visible before
        
        return segments
                    

    def storyboard_lane(self, lane, time_array):
        pool = self.pools[lane]
        for i, note in enumerate(time_array):
            print ("processing {} of lane {}".format(i, lane), end="\r")
            segments = self.get_visible_time_segments(lane, note)
            print ("writing segments for {} of {} {}".format(i, lane, segments))
            for segment in segments:
                sprite = pool.get_free(*segment)
                if sprite is None:
                    print("adding sprite to pool")
                    sprite = self.gear.generate_note(lane)
                    pool.sprites.append(sprite)

                frametime = 1000 / self.framerate
                # print("writing active segment {} to {}".format(*segment))
                for time in arange(*segment, frametime):
                    prev_pos = self.scroll_ctx.get_object_position_at_time(time - frametime, note)
                    prev_screen_pos = self.scroll_to_screen_pos(lane, prev_pos)

                    pos = self.scroll_ctx.get_object_position_at_time(time, note)
                    screen_pos = self.scroll_to_screen_pos(lane, pos)

                    # make use of the fact that variables latch
                    if screen_pos[1] != prev_screen_pos[1]:
                        sprite.move_y(_st=time-frametime, _et=time, 
                                    _sy=prev_screen_pos[1], _ey=screen_pos[1])
                    if screen_pos[0] != prev_screen_pos[0]:
                        sprite.move_y(_st=time-frametime, _et=time, 
                                      _sx=prev_screen_pos[0], _ex=screen_pos[0])

                
                sprite.add_active_period(segment)

    def generate_storyboard(self):
        self.gear.generate_gear()
        
        for lane in range(self.chart.lane_count):
            self.storyboard_lane(lane, map(lambda x: x.time, self.chart.get_lane_objects(lane)))

        for pool in self.pools:
            pool.auto_fade_objects()

if __name__ in "__main__":
    ctx = ScrollCtx([(500, 1), (1500, 2), (2500, 1)], lambda x: 1 if x < 2500 else 2)
    print(ctx.accom_scroll)
    print(250, ctx.get_displacement_at_time(250))
    print(500, ctx.get_displacement_at_time(500))
    print(1000, ctx.get_displacement_at_time(1000))
    print(1500, ctx.get_displacement_at_time(1500))
    print(2000, ctx.get_displacement_at_time(2000))
    print(2500, ctx.get_displacement_at_time(2500))
    print(3000, ctx.get_displacement_at_time(3000))
        
