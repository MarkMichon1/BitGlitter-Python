from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from bitglitter.config.config import SqlBaseClass, engine, session
from bitglitter.utilities.palette import convert_hex_to_rgb, get_color_distance,\
    get_palette_id_from_hash

from datetime import datetime
import math


class Palette(SqlBaseClass):
    __tablename__ = 'palettes'
    __abstract__ = False
    is_valid = Column(Boolean, default=False)
    is_24_bit = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=True)
    is_included_with_repo = Column(Boolean, default=False) # for differentiating other people's colors & our fancy ones

    palette_id = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    nickname = Column(String, unique=True)
    color_set = relationship('PaletteColor', back_populates='palette', cascade='all, delete', passive_deletes=True)
    color_distance = Column(Float, default=0, nullable=False)
    number_of_colors = Column(Integer, default=0, nullable=False)
    bit_length = Column(Integer, default=0, nullable=False)
    datetime_created = Column(DateTime, default=datetime.now())

    @classmethod
    def create(cls, color_set, **kwargs):
        object_ = super().create(**kwargs)
        object_._initialize_colors(color_set)
        return object_

    __table_args__ = (
        UniqueConstraint('palette_id'),
    )

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

    def _convert_colors_to_tuple(self):
        returned_list = []
        for color in self.color_set:
            returned_list.append((color.red_channel, color.green_channel, color.blue_channel))
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
            self.palette_id = get_palette_id_from_hash(self.name, self.description, self.datetime_created,
                                                          color_set_cleaned)

        self.save()


    def return_encoder(self):
        color_set_tupled = self._convert_colors_to_tuple()
        if not self.is_24_bit:
            pass
        else:
            pass

    def return_decoder(self):
        color_set_tupled = self._convert_colors_to_tuple()
        if not self.is_24_bit:
            pass
        else:
            pass

    def return_as_dict(self):
        pass  # below, old data
        return {'name': self.name, 'description': self.description, 'color_set': self.color_set, 'color_distance':
            self.color_distance, 'id': self.palette_id, 'palette_type': self.palette_type, 'number_of_colors':
            self.number_of_colors, 'bit_length': self.bit_length
                }


class PaletteColor(SqlBaseClass):
    __tablename__ = 'palette_colors'
    __abstract__ = False
    palette_id = Column(Integer, ForeignKey('palettes.id'))
    palette = relationship('Palette', back_populates='color_set')
    palette_sequence = Column(Integer, nullable=False)
    red_channel = Column(Integer, nullable=False)
    green_channel = Column(Integer, nullable=False)
    blue_channel = Column(Integer, nullable=False)


SqlBaseClass.metadata.create_all(engine)
