#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2020 fchart authors
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import string
import numpy as np

from time import time

from .label_potential import *
from .astrocalc import *
from .constellation import *
from .mirroring_graphics import *
from .configuration import *
from . import deepsky_object as deepsky

from .graphics_interface import DrawMode

from .widget_mag_scale import WidgetMagnitudeScale
from .widget_map_scale import WidgetMapScale
from .widget_orientation import WidgetOrientation
from .widget_coords import WidgetCoords
from .widget_dso_legend import WidgetDsoLegend
from .widget_telrad import WidgetTelrad

NL = {
    'h':'u',
    'm':'m',
    's':'s',
    'G':'Sterrenstelsel',
    'OCL':'Open sterrenhoop',
    'GCL':'Bolhoop',
    'AST':'Groepje sterren',
    'PN': 'Planetaire nevel',
    'N': 'Diffuse emissienevel',
    'SNR':'Supernovarest',
    'PG':'Deel van sterrenstelsel'
}


EN = {
    'h':'h',
    'm':'m',
    's':'s',
    'G':'Galaxy',
    'OCL':'Open cluster',
    'GCL':'Globular cluster',
    'AST':'Asterism',
    'PN': 'Planetary nebula',
    'N': 'Diffuse nebula',
    'SNR':'Supernova remnant',
    'PG':'Part of galaxy'
}

STAR_LABELS = {
    "alp":"α",
    "bet":"β",
    "gam":"γ",
    "del":"δ",
    "eps":"ε",
    "zet":"ζ",
    "eta":"η",
    "the":"θ",
    "iot":"ι",
    "kap":"κ",
    "lam":"λ",
    "mu":"μ",
    "nu":"ν",
    "xi":"ξ",
    "omi":"ο",
    "pi":"π",
    "rho":"ρ",
    "sig":"σ/ς",
    "tau":"τ",
    "ups":"υ",
    "phi":"φ",
    "chi":"χ",
    "psi":"ψ",
    "ome":"ω"
}

SPEC_TYPE_2_RGB = {
    'O5': (155, 176, 255),
    'O6': (162, 184, 255),
    'O7': (157, 177, 255),
    'O8': (157, 177, 255),
    'O9': (154, 178, 255),
    'O9': (164, 186, 255),
    'B0': (156, 178, 255),
    'B0': (167, 188, 255),
    'B1': (160, 182, 255),
    'B2': (160, 180, 255),
    'B3': (165, 185, 255),
    'B4': (164, 184, 255),
    'B5': (170, 191, 255),
    'B6': (172, 189, 255),
    'B7': (173, 191, 255),
    'B8': (177, 195, 255),
    'B9': (181, 198, 255),
    'A0': (185, 201, 255),
    'A1': (181, 199, 255),
    'A2': (187, 203, 255),
    'A3': (191, 207, 255),
    'A5': (202, 215, 255),
    'A6': (199, 212, 255),
    'A7': (200, 213, 255),
    'A8': (213, 222, 255),
    'A9': (219, 224, 255),
    'F0': (224, 229, 255),
    'F2': (236, 239, 255),
    'F4': (224, 226, 255),
    'F5': (248, 247, 255),
    'F6': (244, 241, 255),
    'F7': (246, 243, 255),
    'F8': (255, 247, 252),
    'F9': (255, 247, 252),
    'G0': (255, 248, 252),
    'G1': (255, 247, 248),
    'G2': (255, 245, 242),
    'G4': (255, 241, 229),
    'G5': (255, 244, 234),
    'G6': (255, 244, 235),
    'G7': (255, 244, 235),
    'G8': (255, 237, 222),
    'G9': (255, 239, 221),
    'K0': (255, 238, 221),
    'K1': (255, 224, 188),
    'K2': (255, 227, 196),
    'K3': (255, 222, 195),
    'K4': (255, 216, 181),
    'K5': (255, 210, 161),
    'K7': (255, 199, 142),
    'K8': (255, 209, 174),
    'M0': (255, 195, 139),
    'M1': (255, 204, 142),
    'M2': (255, 196, 131),
    'M3': (255, 206, 129),
    'M4': (255, 201, 127),
    'M5': (255, 204, 111),
    'M6': (255, 195, 112),
    'M8': (255, 198, 109),
}

STARS_IN_SCALE = 7
LEGEND_MARGIN = 0.47
BASE_SCALE=0.98

#====================>>>  SkymapEngine  <<<====================

class SkymapEngine:

    def __init__(self, graphics, language=EN, ra=0.0, dec=0.0, fieldradius=-1.0, lm_stars=13.8, lm_deepsky=12.5, caption=''):
        """
        Width is width of the map including the legend in mm.
        """
        self.graphics = graphics
        self.config = EngineConfiguration()

        self.caption = ''
        self.language = language
        self.drawingwidth = self.graphics.gi_width
        self.drawingheight = self.graphics.gi_height
        self.min_radius   = 1.0 # of deepsky symbols (mm)

        self.lm_stars     = lm_stars
        self.lm_deepsky   = lm_deepsky
        self.deepsky_label_limit = 15 # deepsky lm for labels

        self.set_caption(caption)
        self.set_field(ra,dec,fieldradius)

        self.active_constellation = None


    def set_field(self, ra, dec, fieldradius):
        """
        Provide the RA, DEC, and radius of the map in radians. This method
        sets a new drawingscale and legend_fontscale
        """
        self.fieldcentre         = (ra,dec)
        self.fieldradius         = fieldradius
        self.fieldsize           = np.sqrt(2.0) * fieldradius

        wh = max(self.drawingwidth, self.drawingheight)

        if self.config.no_margin:
            self.scene_scale = (wh - self.config.legend_linewidth) / wh
        else:
            self.scene_scale = BASE_SCALE

        self.drawingscale    = self.scene_scale * wh /2.0/np.sin(fieldradius)

        self.legend_fontscale    = min(3, wh/100.0)

        self.set_caption(self.caption)


    def set_configuration(self, config):
        self.config = config


    def get_field_radius_mm(self):
        return self.drawingscale * np.sin(self.fieldradius)

    def get_field_rect_mm(self):
        x = self.scene_scale * self.drawingwidth / 2.0
        y = self.scene_scale * self.drawingheight / 2.0
        return (-x, -y, x, y)

    def set_language(self, language):
        """
        Set the language of the legend.
        """
        self.language = language


    def set_caption(self, caption):
        self.caption = caption
        if caption != '':
            self.graphics.set_dimensions(self.drawingwidth,self.drawingheight + self.legend_fontscale*self.graphics.gi_fontsize*2.0)


    def set_active_constellation(self, active_constellation):
        self.active_constellation = active_constellation


    def draw_caption(self):
        if self.caption != '':
            old_size = self.graphics.gi_fontsize
            font_size = self.get_legend_font_size()
            self.graphics.set_font(self.graphics.gi_font, 2.0*font_size)
            self.graphics.text_centred(0,self.drawingwidth/2.0*BASE_SCALE + font_size, self.caption)
            self.graphics.set_font(self.graphics.gi_font, old_size)


    def draw_field_border(self):
        """
        Draw a circle representing the edge of the field of view.
        """
        if self.config.show_field_border:
            self.graphics.set_linewidth(self.config.legend_linewidth)
            x1, y1, x2, y2 = self.get_field_rect_mm()
            self.graphics.line(x1, y1, x1, y2)
            self.graphics.line(x1, y2, x2, y2)
            self.graphics.line(x2, y2, x2, y1)
            self.graphics.line(x2, y1, x1, y1)


    def get_legend_font_size(self):
        return self.config.font_size * self.legend_fontscale


    def draw_widgets(self):
        # Set the fontsize for the entire legend
        fontsize = self.get_legend_font_size()
        self.graphics.set_font(self.graphics.gi_font, fontsize=fontsize)

        x1, y1, x2, y2 = self.get_field_rect_mm()

        if self.config.fov_telrad:
            self.w_telrad.draw(self.graphics)
        if self.config.show_mag_scale_legend:
            self.w_mag_scale.draw(self.graphics, x1, y1, self.config.legend_only)
        if self.config.show_map_scale_legend:
            self.w_map_scale.draw(self.graphics, x2, y1, self.config.legend_only)
        if self.config.show_orientation_legend:
            self.w_orientation.draw(self.graphics, x1, y2, self.config.legend_only)
        if self.config.show_coords_legend:
            self.w_coords.draw(self.graphics, left=x2-fontsize/2, bottom=y2-fontsize, ra=self.fieldcentre[0], dec=self.fieldcentre[1], legend_only=self.config.legend_only)
        if self.config.show_dso_legend:
            self.w_dso_legend.draw_dso_legend(self, self.graphics, self.config.legend_only)


    def draw_deepsky_objects(self, deepsky_catalog, showing_dsos):
        # Draw deep sky
        print('Drawing deepsky...')
        deepsky_list = deepsky_catalog.select_deepsky(self.fieldcentre, self.fieldsize, self.lm_deepsky)
        if showing_dsos:
            for dso in showing_dsos:
                if not dso in deepsky_list:
                    deepsky_list.append(dso)

        deepsky_list.sort(key = lambda x: x.mag)
        deepsky_list_mm = []
        for object in deepsky_list:
            x, y  =  radec_to_xy(object.ra, object.dec, self.fieldcentre, self.drawingscale)
            rlong  = object.rlong*self.drawingscale
            if object.type == deepsky.GALCL:
                rlong = self.min_radius
            if rlong < self.min_radius:
                rlong = self.min_radius
            deepsky_list_mm.append((object, x, y, rlong))

        label_potential = LabelPotential(self.get_field_radius_mm(), deepsky_list_mm)

        print('Drawing objects...')
        for i in range(len(deepsky_list_mm)):
            object, x, y, rlong  = deepsky_list_mm[i]
            rlong  = object.rlong*self.drawingscale
            rshort = object.rshort*self.drawingscale
            posangle=object.position_angle+direction_ddec((object.ra, object.dec), self.fieldcentre)+0.5*np.pi

            if rlong <= self.min_radius:
                rshort *= self.min_radius/rlong
                rlong = self.min_radius

            if object.type == deepsky.GALCL:
                rlong /= 3.0

            label = ''
            if object.messier > 0:
                label = 'M '+str(object.messier)
            elif object.cat == 'NGC':
                object.all_names.sort()
                label = '-'.join(object.all_names)
                if object.mag > self.deepsky_label_limit:
                    label = ''
            else :
                label = object.cat+' '+'-'.join(object.all_names)
                if (not showing_dsos or not object in showing_dsos) and object.mag > self.deepsky_label_limit:
                    label = ''

            label_length = self.graphics.text_width(label)
            labelpos = -1

            labelpos_list =[]
            if object.type == deepsky.G:
                labelpos_list = self.galaxy_labelpos(x, y, rlong, rshort, posangle, label_length)
            elif object.type == deepsky.N:
                labelpos_list = self.diffuse_nebula_labelpos(x, y, 2.0*rlong, 2.0*rshort, posangle, label_length)
            elif object.type in [deepsky.PN,deepsky.OC,deepsky.GC,deepsky.SNR]:
                labelpos_list = self.circular_object_labelpos(x, y, rlong, label_length)
            elif object.type == deepsky.STARS:
                labelpos_list = self.asterism_labelpos(x, y, rlong, label_length)
            else:
                labelpos_list = self.unknown_object_labelpos(x, y, rlong, label_length)

            pot = 1e+30
            for labelpos_index in range(len(labelpos_list)):
                [[x1,y1],[x2,y2],[x3,y3]] = labelpos_list[labelpos_index]
                pot1 = label_potential.compute_potential(x2,y2)
                #label_potential.compute_potential(x1,y1),
                #label_potential.compute_potential(x3,y3)])
                if pot1 < pot:
                    pot = pot1
                    labelpos = labelpos_index

            [xx, yy] = labelpos_list[labelpos][1]
            label_potential.add_position(xx, yy, label_length)

            if object.type == deepsky.G:
                self.galaxy(x, y, rlong, rshort, posangle, label, labelpos)
            elif object.type == deepsky.N:
                self.diffuse_nebula(x, y, 2.0*rlong, 2.0*rshort, posangle, label, labelpos)
            elif object.type == deepsky.PN:
                self.planetary_nebula(x, y, rlong, label, labelpos)
            elif object.type == deepsky.OC:
                self.open_cluster(x, y, rlong, label, labelpos)
            elif object.type == deepsky.GC:
                self.globular_cluster(x, y, rlong, label, labelpos)
            elif object.type == deepsky.STARS:
                self.asterism(x, y, rlong, label, labelpos)
            elif object.type == deepsky.SNR:
                self.supernova_remnant(x, y, rlong, label, labelpos)
            else:
                self.unknown_object(x, y, rlong, label, labelpos)


    def draw_extra_objects(self,extra_positions):
        # Draw extra objects
        print('Drawing extra objects...')
        for object in extra_positions:
            rax,decx,label,labelpos = object
            if angular_distance((rax,decx),self.fieldcentre) < self.fieldsize:
                x, y =  radec_to_xy(rax, decx, self.fieldcentre, self.drawingscale)
                self.unknown_object(x,y,self.min_radius,label,labelpos)

    def draw_highlights(self, highlights):
        # Draw extra objects
        print('Drawing highlights...')
        for hi in highlights:
            rax, decx = hi
            if angular_distance((rax,decx),self.fieldcentre) < self.fieldsize:
                x, y =  radec_to_xy(rax,decx, self.fieldcentre, self.drawingscale)
                self.highlight_cross(x,y)

    def draw_trajectory(self,trajectory):
        # Draw extra objects
        print('Drawing trajectory...')
        self.graphics.save()
        self.graphics.set_linewidth(self.config.constellation_linewidth)
        self.graphics.set_pen_rgb(self.config.dso_color)

        fh = self.graphics.gi_fontsize
        label1 = ''
        x1 = None
        y1 = None

        for i in range(0, len(trajectory)-1):
            rax2, decx2, label2 = trajectory[i]
            x2,y2,z2 =  radec_to_xyz(rax2,decx2, self.fieldcentre, self.drawingscale)

            if i > 0:
                self.mirroring_graphics.line(x1, y1, x2, y2)

            self.unknown_object(x1, y1, self.min_radius, label2, '')

            x1,y1,z1 = (x2, y2,z2)
            label1 = label2

        self.graphics.restore()

    def magnitude_to_radius(self, magnitude):
        #radius = 0.13*1.35**(int(self.lm_stars)-magnitude)
        mag_scale_x = [0, 1, 2,   3,   4,    5, 25]
        mag_scale_y = [0, 2, 3.5, 4.5, 5.25, 6, 15]

        mag_d = self.lm_stars - np.clip(magnitude, a_min=None, a_max=self.lm_stars)
        mag_s = np.interp(mag_d, mag_scale_x, mag_scale_y)

        radius = 0.15 * 1.33 ** (mag_s)
        return radius

    def draw_stars(self, star_catalog):
        # Select and draw stars
        print('Drawing stars...')
        selection = star_catalog.select_stars(self.fieldcentre, self.fieldsize, self.lm_stars)
        print(str(selection.shape[0]) + ' stars in map.')
        print('Faintest star: ' + str(int(max(selection['mag'])*100.0 + 0.5)/100.0))

        x, y = radec_to_xy(selection['ra'], selection['dec'], self.fieldcentre, self.drawingscale)

        mag       = selection['mag']
        spec_type = selection['spec_type']

        indices   = argsort(mag)
        magsorted = mag[indices]
        xsorted   = x[indices]
        ysorted   = y[indices]
        spec_type_sorted = spec_type[indices]

        rsorted = self.magnitude_to_radius(magsorted)

        self.graphics.set_linewidth(0)

        for i in range(len(xsorted)):
            self.star(xsorted[i], ysorted[i], rsorted[i], spec_type_sorted[i])


    def draw_constellations(self, constell_catalog):
        print('Drawing constellations...' + str(self.fieldcentre[0]))
        self.draw_constellation_boundaries(constell_catalog)
        self.draw_constellation_shapes(constell_catalog)
        self.draw_constellation_stars(constell_catalog)

    def in_field(self, ra, dec):
        ra_sep = abs(ra-self.fieldcentre[0])
        if ra_sep > np.pi:
            ra_sep = 2*np.pi-ra_sep

        return ra_sep * np.cos(dec) < self.fieldsize and abs(dec-self.fieldcentre[1]) < self.fieldsize

    def draw_constellation_stars(self, constell_catalog):
        if not self.config.show_star_labels:
            return
        fn = self.graphics.gi_fontsize
        printed = {}
        star_ra = []
        star_dec = []
        star_label_mag = []
        for star in constell_catalog.bright_stars:
            slabel = star.greek
            if slabel == '' and self.config.show_flamsteed and star.constellation != '' and star.constell_number != '':
                slabel = star.constell_number + ' ' + star.constellation.lower().capitalize()
            if not slabel:
                continue

            printed_labels = printed.get(star.constellation)

            if not printed_labels:
                printed_labels = set()
                printed[star.constellation] = printed_labels
            elif slabel in printed_labels:
                continue

            printed_labels.add(slabel)

            big_label = slabel in STAR_LABELS
            if big_label:
                slabel = STAR_LABELS.get(slabel)

            star_ra.append(star.ra)
            star_dec.append(star.dec)
            star_label_mag.append((big_label, slabel, star.mag))

        x, y, z = radec_to_xyz(np.array(star_ra), np.array(star_dec), self.fieldcentre, self.drawingscale)

        for i in range(len(x)):
            if z[i] > 0:
                if star_label_mag[i][0]:
                    self.graphics.set_font(self.graphics.gi_font, 1.3*fn)
                else:
                    self.graphics.set_font(self.graphics.gi_font, 0.9*fn)
                r = self.magnitude_to_radius(star_label_mag[i][2])
                self.draw_circular_object_label(x[i], y[i], r, star_label_mag[i][1])

        self.graphics.set_font(self.graphics.gi_font, fn)


    def draw_constellation_shapes(self, constell_catalog):
        self.graphics.save()
        self.graphics.set_linewidth(self.config.constellation_linewidth)
        self.graphics.set_pen_rgb(self.config.constellation_lines_color)

        x1, y1, z1 = radec_to_xyz(constell_catalog.all_constell_lines[:,0], constell_catalog.all_constell_lines[:,1], self.fieldcentre, self.drawingscale)
        x2, y2, z2 = radec_to_xyz(constell_catalog.all_constell_lines[:,2], constell_catalog.all_constell_lines[:,3], self.fieldcentre, self.drawingscale)

        for i in range(len(x1)):
            if z1[i] > 0 and z2[i] > 0:
                self.mirroring_graphics.line(x1[i], y1[i], x2[i], y2[i])

        self.graphics.restore()


    def draw_constellation_boundaries(self, constell_catalog):
        self.graphics.save()
        self.graphics.set_dashed_line(1.2, 1.2)
        self.graphics.set_linewidth(self.config.constellation_linewidth)
        self.graphics.set_pen_rgb(self.config.constellation_border_color)

        x1, y1, z1 = radec_to_xyz(constell_catalog.boundaries[:,0], constell_catalog.boundaries[:,1], self.fieldcentre, self.drawingscale)
        x2, y2, z2 = radec_to_xyz(constell_catalog.boundaries[:,2], constell_catalog.boundaries[:,3], self.fieldcentre, self.drawingscale)

        for i in range(len(x1)):
            if z1[i] > 0 and z2[i] > 0:
                self.mirroring_graphics.line(x1[i], y1[i], x2[i], y2[i])

        self.graphics.restore()


    def make_map(self, used_catalogs, showing_dsos=None, highlights=[], extra_positions=[], trajectory=[] ):

        # tm = time()

        if self.config.mirror_x or self.config.mirror_y:
            self.mirroring_graphics = MirroringGraphics(self.graphics, self.config.mirror_x, self.config.mirror_y)
        else:
            self.mirroring_graphics = self.graphics

        self.create_widgets()

        self.graphics.set_background_rgb(self.config.background_color)

        self.graphics.new()

        if not self.config.legend_only:
            self.graphics.clear()

        self.graphics.set_pen_rgb(self.config.draw_color)
        self.graphics.set_fill_rgb(self.config.draw_color)
        self.graphics.set_font(font=self.config.font, fontsize=self.config.font_size)
        self.graphics.set_linewidth(self.config.legend_linewidth)

        x1, y1, x2, y2 = self.get_field_rect_mm()

        w_mags_width, w_mags_heigth = self.w_mag_scale.get_size()
        w_maps_width, w_maps_height = self.w_map_scale.get_size()

        if not self.config.legend_only:
            clip_path = [(x2,y2)]
            if self.config.show_map_scale_legend:
                clip_path.extend([(x2,y1+w_maps_height),
                                 (x2-w_maps_width, y1+w_maps_height),
                                 (x2-w_maps_width, y1)])
            else:
                clip_path.append((x2,y1))

            if self.config.show_mag_scale_legend:
                clip_path.extend([(x1 + w_mags_width, y1),
                                 (x1 + w_mags_width, y1 + w_mags_heigth),
                                 (x1, y1 + w_mags_heigth)])
            else:
                clip_path.append((x1, y1))

            clip_path.append((x1, y2))

            self.graphics.clip_path(clip_path)

            if highlights != []:
                self.draw_highlights(highlights)

            if used_catalogs.constellcatalog != None:
                self.draw_constellations(used_catalogs.constellcatalog)
                # print("constellations within {} ms".format(str(time()-tm)), flush=True)
                # tm = time()
            if used_catalogs.deepskycatalog != None:
                self.draw_deepsky_objects(used_catalogs.deepskycatalog, showing_dsos)
                # print("DSO within {} ms".format(str(time()-tm)), flush=True)
                # tm = time()
            if extra_positions != []:
                self.draw_extra_objects(extra_positions)
            if trajectory != []:
                self.draw_trajectory(trajectory)
            if used_catalogs.starcatalog != None:
                self.draw_stars(used_catalogs.starcatalog)
                # print("Stars within {} ms".format(str(time()-tm)), flush=True)
                # tm = time()

            self.graphics.reset_clip()

        print('Drawing legend')
        self.draw_caption()

        print('Drawing widgets')
        self.draw_widgets()

        # Draw border of field-of-view
        self.draw_field_border()

        self.graphics.finish()
        # print("Rest {} ms".format(str(time()-tm)), flush=True)

    def create_widgets(self):
        self.w_mag_scale = WidgetMagnitudeScale(self,
                                          legend_fontsize=self.get_legend_font_size(),
                                          stars_in_scale=STARS_IN_SCALE,
                                          lm_stars=self.lm_stars,
                                          legend_linewidth=self.config.legend_linewidth)

        self.w_map_scale = WidgetMapScale(drawingscale=self.drawingscale,
                                    maxlength=self.drawingwidth/3.0,
                                    legend_fontsize=self.get_legend_font_size(),
                                    legend_linewidth=self.config.legend_linewidth)

        self.w_orientation = WidgetOrientation(legend_fontsize=self.get_legend_font_size(),
                                               mirror_x=self.config.mirror_x,
                                               mirror_y=self.config.mirror_y
                                               )

        self.w_coords = WidgetCoords(self.language)

        self.w_dso_legend = WidgetDsoLegend(self.language, self.drawingwidth, LEGEND_MARGIN)

        self.w_telrad = WidgetTelrad(self.drawingscale, self.config.constellation_linewidth)


    def star(self, x, y, radius, spec_type):
        """
        Filled circle with boundary. Set fill colour and boundary
        colour in advance using set_pen_rgb and set_fill_rgb
        """
        star_color_n = SPEC_TYPE_2_RGB.get(chr(spec_type[0]) + str(round(spec_type[1]/10)), (255, 255, 255))
        star_color = (star_color_n[0]/255, star_color_n[1]/255, star_color_n[2]/255)
        self.graphics.set_pen_rgb((star_color[0]/3, star_color[0]/3, star_color[0]/3))
        self.graphics.set_fill_rgb(star_color)

        r = int((radius + self.graphics.gi_linewidth/2.0)*100.0 + 0.5)/100.0
        self.mirroring_graphics.circle(x, y, r,DrawMode.BOTH)


    def no_mirror_star(self, x, y, radius):
        """
        Filled circle with boundary. Set fill colour and boundary
        colour in advance using set_pen_rgb and set_fill_rgb
        """
        r = int((radius + self.graphics.gi_linewidth/2.0)*100.0 + 0.5)/100.0
        self.graphics.circle(x, y, r,DrawMode.BOTH)

    def open_cluster(self, x, y, radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0

        self.graphics.save()

        self.graphics.set_pen_rgb(self.config.star_cluster_color)
        self.graphics.set_linewidth(self.config.open_cluster_linewidth)
        self.graphics.set_dashed_line(0.6, 0.4)

        self.mirroring_graphics.circle(x,y,r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()


    def asterism(self,x,y,radius=-1, label='', labelpos=-1):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        w2=2**0.5
        d = r/2.0*w2

        self.graphics.save()

        self.graphics.set_pen_rgb(self.config.star_cluster_color)
        self.graphics.set_linewidth(self.config.open_cluster_linewidth)
        self.graphics.set_dashed_line(0.6, 0.4)

        diff = self.graphics.gi_linewidth/2.0/w2

        self.mirroring_graphics.line(x-diff, y+d+diff, x+d+diff,y-diff)
        self.mirroring_graphics.line(x+d, y, x,y-d)
        self.mirroring_graphics.line(x+diff, y-d-diff, x-d-diff,y+diff)
        self.mirroring_graphics.line(x-d, y, x,y+d)

        fh =  self.graphics.gi_fontsize
        if label != '':
            self.mirroring_graphics.set_pen_rgb(self.config.label_color)
            if labelpos == 0 or labelpos == -1:
                self.mirroring_graphics.text_centred(x, y-d-2*fh/3.0, label)
            elif labelpos == 1:
                self.mirroring_graphics.text_centred(x, y+d+fh/3.0, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_left(x-d-fh/6.0, y-fh/3.0, label)
            elif labelpos == 3:
                self.mirroring_graphics.text_right(x+d+fh/6.0, y-fh/3.0, label)
        self.graphics.restore()


    def asterism_labelpos(self,x,y,radius=-1,label_length=0.0):
        """
        x,y,radius, label_length in mm
        returns [[start, centre, end],()]
        """
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        w2 = 2**0.5
        d = r/2.0*w2
        fh =  self.graphics.gi_fontsize
        label_pos_list = []
        yy = y-d-2*fh/3.0
        label_pos_list.append([[x-label_length/2.0,yy],[x,yy],[x+label_length,yy]])
        yy = y+d+2*fh/3.0
        label_pos_list.append([[x-label_length/2.0,yy],[x,yy],[x+label_length,yy]])
        xx = x-d-fh/6.0
        yy = y
        label_pos_list.append([[xx-label_length,yy],[xx-label_length/2.0,yy],[xx,yy]])
        xx = x+d+fh/6.0
        yy = y
        label_pos_list.append([[xx,yy],[xx+label_length/2.0,yy],[xx+label_length,yy]])
        return label_pos_list


    def galaxy(self, x, y, rlong=-1, rshort=-1, posangle=0.0, label='', labelpos=-1):
        """
        If rlong != -1 and rshort == -1 =>   rshort <- rlong
        if rlong < 0.0 => standard galaxy
        labelpos can be 0,1,2,3
        """
        rl = rlong
        rs = rshort
        if rlong <= 0.0:
            rl = self.drawingwidth/40.0
            rs = rl/2.0
        if rlong > 0.0 and rshort < 0.0:
            rl = rlong
            rs = rlong/2.0

        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_pen_rgb(self.config.galaxy_color)

        p = posangle
        if posangle >= 0.5*np.pi:
            p += np.pi
        if posangle < -0.5*np.pi:
            p -= np.pi

        fh = self.graphics.gi_fontsize
        self.mirroring_graphics.ellipse(x,y,rl, rs, p)

        if label != '':
            self.graphics.save()
            self.mirroring_graphics.translate(x,y)
            self.mirroring_graphics.rotate(p)
            self.mirroring_graphics.set_pen_rgb(self.config.label_color)
            if labelpos == 0 or labelpos == -1:
                self.graphics.text_centred(0, -rshort-0.5*fh, label)
            elif labelpos == 1:
                self.graphics.text_centred(0, +rshort+0.5*fh, label)
            elif labelpos == 2:
                self.graphics.text_right(rlong+fh/6.0, -fh/3.0, label)
            elif labelpos == 3:
                self.graphics.text_left(-rlong-fh/6.0, -fh/3.0, label)
            self.graphics.restore()

        self.graphics.restore()


    def galaxy_labelpos(self,x,y,rlong=-1,rshort=-1,posangle=0.0,label_length=0.0):
        rl = rlong
        rs = rshort
        if rlong <= 0.0:
            rl = self.drawingwidth/40.0
            rs = rl/2.0
        if rlong > 0.0 and rshort < 0.0:
            rl = rlong
            rs = rlong/2.0

        p = posangle
        if posangle >= 0.5*np.pi:
            p += np.pi
        if posangle < -0.5*np.pi:
            p -= np.pi

        fh = self.graphics.gi_fontsize
        label_pos_list = []

        sp = np.sin(p)
        cp = np.cos(p)

        hl = label_length/2.0

        d = -rshort-0.5*fh
        xc = x + d*sp
        yc = y - d*cp
        xs = xc -hl*cp
        ys = yc -hl*sp
        xe = xc +hl*cp
        ye = yc +hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        xc = x - d*sp
        yc = y + d*cp
        xs = xc -hl*cp
        ys = yc -hl*sp
        xe = xc +hl*cp
        ye = yc +hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        d  = rlong+fh/6.0
        xs = x + d*cp
        ys = y + d*sp
        xc = xs + hl*cp
        yc = ys + hl*sp
        xe = xc + hl*cp
        ye = yc + hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        xe = x - d*cp
        ye = y - d*sp
        xc = xe - hl*cp
        yc = ye - hl*sp
        xs = xc - hl*cp
        ys = yc - hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        return label_pos_list


    def draw_circular_object_label(self, x, y, r, label, labelpos=-1):
        fh = self.graphics.gi_fontsize
        if label:
            self.mirroring_graphics.set_pen_rgb(self.config.label_color)
            arg = 1.0-2*fh/(3.0*r)
            if arg < 1.0 and arg > -1.0:
                a = np.arccos(arg)
            else:
                a = 0.5*np.pi
            if labelpos == 0 or labelpos == -1:
                self.mirroring_graphics.text_right(x+np.sin(a)*r+fh/6.0, y-r, label)
            elif labelpos == 1:
                self.mirroring_graphics.text_left(x-np.sin(a)*r-fh/6.0, y-r, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_right(x+np.sin(a)*r+fh/6.0, y+r-2*fh/3.0, label)
            elif labelpos == 3:
                self.mirroring_graphics.text_left(x-np.sin(a)*r-fh/6.0, y+r-2*fh/3.0, label)


    def circular_object_labelpos(self, x, y, radius=-1.0, label_length=0.0):
        fh = self.graphics.gi_fontsize
        r = radius

        if radius <= 0.0:
            r = self.drawingwidth/40.0

        arg = 1.0-2*fh/(3.0*r)

        if arg < 1.0 and arg > -1.0:
            a = np.arccos(arg)
        else:
            a = 0.5*np.pi

        label_pos_list = []
        xs = x+np.sin(a)*r+fh/6.0
        ys = y-r+fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        xs = x-np.sin(a)*r-fh/6.0 - label_length
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x+np.sin(a)*r+fh/6.0
        ys = y+r-fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x+np.sin(a)*r+fh/6.0
        ys = y+r-fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list



    def globular_cluster(self, x,y,radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_pen_rgb(self.config.star_cluster_color)

        self.mirroring_graphics.circle(x,y,r)
        self.mirroring_graphics.line(x-r, y, x+r, y)
        self.mirroring_graphics.line(x, y-r, x, y+r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()


    def diffuse_nebula(self, x, y, width=-1.0, height=-1.0, posangle=0.0, label='',labelpos=''):
        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_pen_rgb(self.config.nebula_color)

        d = 0.5*width
        if width < 0.0:
            d = self.drawingwidth/40.0
        d1 = d+self.graphics.gi_linewidth/2.0

        self.mirroring_graphics.line(x-d1, y+d, x+d1, y+d)
        self.mirroring_graphics.line(x+d, y+d, x+d, y-d)
        self.mirroring_graphics.line(x+d1, y-d, x-d1, y-d)
        self.mirroring_graphics.line(x-d, y-d, x-d, y+d)

        fh = self.graphics.gi_fontsize
        if label != '':
            self.mirroring_graphics.set_pen_rgb(self.config.label_color)
            if labelpos == 0 or labelpos == -1:
                self.mirroring_graphics.text_centred(x, y-d-fh/2.0, label)
            elif labelpos == 1:
                self.mirroring_graphics.text_centred(x, y+d+fh/2.0, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_left(x-d-fh/6.0, y-fh/3.0, label)
            elif labelpos == 3:
                self.mirroring_graphics.text_right(x+d+fh/6.0, y-fh/3.0, label)
        self.graphics.restore()


    def diffuse_nebula_labelpos(self, x, y, width=-1.0, height=-1.0, posangle=0.0, label_length=0.0):

        d = 0.5*width
        if width < 0.0:
            d = self.drawingwidth/40.0
        fh = self.graphics.gi_fontsize

        label_pos_list = []
        xs = x - label_length/2.0
        ys = y-d-fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        ys = y+d+fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x - d - fh/6.0 - label_length
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x + d + fh/6.0
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list


    def planetary_nebula(self, x, y, radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/60.0
        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_pen_rgb(self.config.nebula_color)

        self.mirroring_graphics.circle(x,y,0.75*r)
        self.mirroring_graphics.line(x-0.75*r, y, x-1.5*r, y)
        self.mirroring_graphics.line(x+0.75*r, y, x+1.5*r, y)
        self.mirroring_graphics.line(x, y+0.75*r, x, y+1.5*r)
        self.mirroring_graphics.line(x, y-0.75*r, x, y-1.5*r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()


    def supernova_remnant(self, x, y, radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_pen_rgb(self.config.nebula_color)

        self.mirroring_graphics.circle(x,y,r-self.graphics.gi_linewidth/2.0)
        #self.graphics.circle(x,y,r*0.85)
        #self.graphics.circle(x,y,r*0.7)
        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()

    def unknown_object(self, x, y, radius=-1.0, label='',labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0

        r /= 2**0.5
        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_pen_rgb(self.config.dso_color)

        self.mirroring_graphics.line(x-r, y+r, x+r, y-r)
        self.mirroring_graphics.line(x+r, y+r, x-r, y-r)

        fh = self.graphics.gi_fontsize

        if label != '':
            self.mirroring_graphics.set_pen_rgb(self.config.label_color)
            if labelpos == 0:
                self.mirroring_graphics.text_right(x+r+fh/6.0, y-fh/3.0, label)
            elif labelpos ==1:
                self.mirroring_graphics.text_left(x-r-fh/6.0, y-fh/3.0, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_centred(x, y+ r + fh/2.0, label)
            else:
                self.mirroring_graphics.text_centred(x, y - r - fh/2.0, label)
        self.graphics.restore()


    def unknown_object_labelpos(self, x, y, radius=-1, label_length=0.0):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        fh = self.graphics.gi_fontsize
        r/=2**0.5
        label_pos_list = []
        xs = x + r +fh/6.0
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x - r -fh/6.0 - label_length
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x -label_length/2.0
        ys = y + r +fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x -label_length/2.0
        ys = y - r -fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list


    def highlight_cross(self, x, y):
        self.graphics.save()

        r = 2 * self.config.font_size

        self.graphics.set_linewidth(self.config.dso_linewidth * 1.5)
        self.graphics.set_pen_rgb(self.config.highlight_color)

        self.mirroring_graphics.line(x-r, y, x-r/2, y)
        self.mirroring_graphics.line(x+r, y, x+r/2, y)
        self.mirroring_graphics.line(x, y+r, x, y+r/2)
        self.mirroring_graphics.line(x, y-r, x, y-r/2)

        self.graphics.restore()


if __name__ == '__main__':
    from . import cairo
    from . import composite_star_catalog as sc

    data_dir='./data/catalogs/'

    stars = sc.CompositeStarCatalog(data_dir)

    width = 200
    cairo = cairo.CairoDrawing(width, width, 'radec00.pdf',)

    sm = SkymapEngine(cairo)
    sm.set_caption('Probeersel')
    sm.set_field(1.5,1, 0.05)
    sm.make_map(stars)
    cairo.close()

