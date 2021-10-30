from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from bitglitter.config.config import engine, session, SQLBaseClass
from bitglitter.utilities.palette import BitsToColor, ColorsToBits, convert_hex_to_rgb, get_color_distance, \
    get_palette_id_from_hash

import base64
import math
import time


class Palette(SQLBaseClass):
    __tablename__ = 'palettes'
    __abstract__ = False
    is_24_bit = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=True)
    is_included_with_repo = Column(Boolean, default=False)  # for differentiating other people's colors & our fancy ones

    palette_id = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    nickname = Column(String, unique=True)
    color_set = Column(String)
    color_distance = Column(Float, default=0, nullable=False)
    number_of_colors = Column(Integer, default=0, nullable=False)
    bit_length = Column(Integer, default=0, nullable=False)
    time_created = Column(Integer, default=time.time)
    base64_string = Column(String)

    @classmethod
    def create(cls, color_set, **kwargs):
        object_ = super().create(**kwargs)
        object_._initialize_colors(color_set)
        if object_.is_custom:
            assembled_string = '\\\\'.join(
                [object_.palette_id, object_.name, object_.description, str(object_.time_created),
                 str(object_.convert_colors_to_tuple())]) + '\\\\'
            object_.base64_string = base64.b64encode(assembled_string.encode()).decode()
        object_.save()
        return object_

    __table_args__ = (
        UniqueConstraint('palette_id'),
    )

    def __str__(self):
        palette_type = 'Custom' if self.is_custom else 'Default'
        return f'{palette_type} Palette - {self.name} - {self.number_of_colors} Colors'

    def _calculate_palette_math(self, color_set, save=True):
        """Runs during model creation and when color set is updated."""

        self.color_distance = get_color_distance(color_set)
        self.number_of_colors = len(color_set)
        is_valid = math.log2(self.number_of_colors).is_integer()
        if is_valid:
            self.bit_length = int(math.log(self.number_of_colors, 2))
        else:
            self.bit_length = 0
        self.is_valid = is_valid

        if save:  # Added to prevent repetitive saves if used in other methods
            self.save()

    def convert_colors_to_tuple(self):
        """Since all of their colors are stored as a single string for speed, this function retrieves it and returns
        them in a more usable list format.
        """

        if not self.is_24_bit:
            string_split = self.color_set.split('|')
            returned_list = []
            for piece in string_split:
                channels = piece.split(',')
                channels = [int(channel) for channel in channels]
                returned_list.append((channels[0], channels[1], channels[2]))
            return returned_list
        else:
            return None

    def _initialize_colors(self, color_set):
        """An internal method that blindly accepts tuples.  Use palettefunctions functions for prior necessary
        validation of values.
        """

        color_set_cleaned = convert_hex_to_rgb(color_set) if color_set else None
        if not self.is_24_bit:
            self._calculate_palette_math(color_set_cleaned, save=False)

            string_list = []
            for color in color_set_cleaned:
                to_string = [str(channel) for channel in color]
                string_list.append(','.join(to_string))

            self.color_set = '|'.join(string_list)
        else:
            self.bit_length = 24
            self.color_distance = 0
            self.number_of_colors = 16777216

        if self.is_custom:
            self.palette_id = get_palette_id_from_hash(self.name, self.description, self.time_created,
                                                       color_set_cleaned)

    def return_encoder(self):
        color_set_tupled = self.convert_colors_to_tuple()
        return BitsToColor(color_set_tupled, self.bit_length, self.name)

    def return_decoder(self):
        color_set_tupled = self.convert_colors_to_tuple()
        return ColorsToBits(color_set_tupled, self.bit_length, self.name)


SQLBaseClass.metadata.create_all(engine)
