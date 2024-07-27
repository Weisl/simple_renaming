"""
Copyright (C) 2019 Matthias Patscheider
patscheider.matthias@gmail.com

Created by Matthias Patscheider

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# support reloading sub-modules
if "bpy" in locals():
    import importlib

    importlib.reload(add_suffix_panel)
    importlib.reload(operators)
    importlib.reload(preferences)
    importlib.reload(ui)
    importlib.reload(validation)
    importlib.reload(variable_replacer)

else:
    from . import add_suffix_panel
    from . import operators
    from . import preferences
    from . import ui
    from . import name_vallidation
    from . import variable_replacer



files = [
    add_suffix_panel,
    operators,
    ui,
    name_vallidation,

    # keymap and preferences should be last
    preferences,
]


def register():
    for file in files:
        file.register()


def unregister():
    for file in reversed(files):
        file.unregister()


if __name__ == "__main__":
    register()
