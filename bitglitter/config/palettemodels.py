from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from bitglitter.config.config import engine, session, SqlBaseClass
from bitglitter.utilities.palette import BitsToColor, ColorsToBits, convert_hex_to_rgb, get_color_distance, \
    get_palette_id_from_hash

import math
import time


class Palette(SqlBaseClass):
    __tablename__ = 'palettes'
    __abstract__ = False
    is_valid = Column(Boolean, default=False)
    is_24_bit = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=True)
    is_included_with_repo = Column(Boolean, default=False)  # for differentiating other people's colors & our fancy ones

    palette_id = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    nickname = Column(String, unique=True)
    color_set = relationship('PaletteColor', back_populates='palette', cascade='all, delete', passive_deletes=True)
    color_distance = Column(Float, default=0, nullable=False)
    number_of_colors = Column(Integer, default=0, nullable=False)
    bit_length = Column(Integer, default=0, nullable=False)
    time_created = Column(Integer, default=time.time)

    @classmethod
    def create(cls, color_set, **kwargs):
        object_ = super().create(**kwargs)
        object_._initialize_colors(color_set)
        return object_

    __table_args__ = (
        UniqueConstraint('palette_id'),
    )

    def __str__(self):
        palette_type = 'Custom' if self.is_custom else 'Default'
        return f'{palette_type} Palette - {self.name} - {self.number_of_colors} Colors'

    def _calculate_palette_math(self, color_set, save=True):
        """Runs during model creation and when color set is updated."""

        if not self.is_24_bit:
            self.color_distance = get_color_distance(color_set)
            self.number_of_colors = len(color_set)
            is_valid = math.log2(self.number_of_colors).is_integer()
            if is_valid:
                self.bit_length = int(math.log(self.number_of_colors, 2))
            else:
                self.bit_length = 0
            self.is_valid = is_valid
        else:
            self.bit_length = 24
            self.color_distance = 0
            self.number_of_colors = 16777216

        if save:  # Added to prevent repetitive saves if used in other methods
            self.save()

    def convert_colors_to_tuple(self):
        """Since each of their colors are their own PaletteColor object, this function retrieves them and returns them
        in a more usable format.
        """

        returned_list = []
        for color in self.color_set:
            returned_list.append(color.return_rgb_tuple())
        return returned_list

    def _initialize_colors(self, color_set):
        """An internal method that blindly accepts tuples.  Use palettefunctions functions for prior necessary
        validation of values.
        """

        color_set_cleaned = convert_hex_to_rgb(color_set) if color_set else None
        if not self.is_24_bit:
            self._calculate_palette_math(color_set_cleaned, save=False)
            sequence_number = 0
            color_objects = []
            for color in color_set_cleaned:
                color_objects.append(PaletteColor(palette_id=self.id, palette_sequence=sequence_number,
                                                  red_channel=color[0], green_channel=color[1], blue_channel=color[2]))
                sequence_number += 1
            session.bulk_save_objects(color_objects)
        if self.is_custom:
            self.palette_id = get_palette_id_from_hash(self.name, self.description, self.time_created,
                                                       color_set_cleaned)

        self.save()

    def return_encoder(self, palette_type):
        color_set_tupled = self.convert_colors_to_tuple()
        return BitsToColor(color_set_tupled, self.bit_length, palette_type)

    def return_decoder(self):
        color_set_tupled = self.convert_colors_to_tuple()
        return ColorsToBits(color_set_tupled)


class PaletteColor(SqlBaseClass):
    __tablename__ = 'palette_colors'
    __abstract__ = False
    palette_id = Column(Integer, ForeignKey('palettes.id'))
    palette = relationship('Palette', back_populates='color_set')
    palette_sequence = Column(Integer, nullable=False)
    red_channel = Column(Integer, nullable=False)
    green_channel = Column(Integer, nullable=False)
    blue_channel = Column(Integer, nullable=False)

    def __str__(self):
        return f'Color for {self.palette.name} - ({self.red_channel}, {self.green_channel}, {self.blue_channel}) ' \
               f'- {self.palette_sequence} seq'

    def return_rgb_tuple(self):
        return self.red_channel, self.green_channel, self.blue_channel


SqlBaseClass.metadata.create_all(engine)
