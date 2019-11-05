# The MIT License (MIT)
#
# Copyright (c) 2019 - ∞ Mark Michon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ===============================================================================
#
# Official project page (Python library):
# https://github.com/MarkMichon1/BitGlitter
#
# Official project page (Executable GUI)
# https://github.com/MarkMichon1/BitGlitter-GUI
#
# Guides and roadmap (under construction!):
# https://github.com/MarkMichon1/BitGlitter/wiki
#
# Discord channel:
# https://discord.gg/t9uv2pZ
#
# Have fun! :)
#
#   - Mark
# ===============================================================================

# CORE USES
from bitglitter.write.write import write
from bitglitter.read.read import read


# GENERAL CONFIGURATION
from bitglitter.config.configfunctions import clear_session, clear_stats, output_stats


# PARTIAL SAVE CONTROL
from bitglitter.read.savedfilefunctions import begin_assembly, print_full_save_list, remove_partial_save, \
    update_partial_save, remove_all_partial_saves


# CUSTOM PALETTE
from bitglitter.palettes.palettefunctions import add_custom_palette, edit_nickname_to_custom_palette, \
    clear_all_custom_palettes, clear_custom_palette_nicknames, print_full_palette_list, remove_custom_palette, \
    remove_custom_palette_nickname

# GUI interface
# TBA