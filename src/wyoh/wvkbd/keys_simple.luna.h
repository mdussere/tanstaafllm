/* Wyoh Step 6: Luna's AZERTY "simple" layer for wvkbd 0.15.
 *
 * Replaces `keys_simple[]` in wvkbd's layout.mobintl.h (GPL-3.0-or-later,
 * like wvkbd) when build_wvkbd_luna.sh makes layout.luna.h. Four rows of ten
 * units for a 720 x 240 keyboard: French letter order, the common French
 * accents on the letter layer, Shift, Backspace, the next-layer key (digits
 * and symbols: wvkbd's "special" layer), space and Enter. Accents are `Copy`
 * keys (wvkbd types the code point), so they do not depend on a keymap.
 */
static struct key keys_simple[] = {
  {"a", "A", 1.0, Code, KEY_A, &layouts[ComposeA]},
  {"z", "Z", 1.0, Code, KEY_Z, &layouts[ComposeZ]},
  {"e", "E", 1.0, Code, KEY_E, &layouts[ComposeE]},
  {"r", "R", 1.0, Code, KEY_R, &layouts[ComposeR]},
  {"t", "T", 1.0, Code, KEY_T, &layouts[ComposeT]},
  {"y", "Y", 1.0, Code, KEY_Y, &layouts[ComposeY]},
  {"u", "U", 1.0, Code, KEY_U, &layouts[ComposeU]},
  {"i", "I", 1.0, Code, KEY_I, &layouts[ComposeI]},
  {"o", "O", 1.0, Code, KEY_O, &layouts[ComposeO]},
  {"p", "P", 1.0, Code, KEY_P, &layouts[ComposeP]},
  {"", "", 0.0, EndRow},

  {"q", "Q", 1.0, Code, KEY_Q, &layouts[Emoji]},
  {"s", "S", 1.0, Code, KEY_S, &layouts[ComposeS]},
  {"d", "D", 1.0, Code, KEY_D, &layouts[ComposeD]},
  {"f", "F", 1.0, Code, KEY_F, &layouts[ComposeF]},
  {"g", "G", 1.0, Code, KEY_G, &layouts[ComposeG]},
  {"h", "H", 1.0, Code, KEY_H, &layouts[ComposeH]},
  {"j", "J", 1.0, Code, KEY_J, &layouts[ComposeJ]},
  {"k", "K", 1.0, Code, KEY_K, &layouts[ComposeK]},
  {"l", "L", 1.0, Code, KEY_L, &layouts[ComposeL]},
  {"m", "M", 1.0, Code, KEY_M, &layouts[ComposeM]},
  {"", "", 0.0, EndRow},

  {"⇧", "⇫", 1.0, Mod, Shift, .scheme = 1},
  {"w", "W", 1.0, Code, KEY_W, &layouts[ComposeW]},
  {"x", "X", 1.0, Code, KEY_X, &layouts[ComposeX]},
  {"c", "C", 1.0, Code, KEY_C, &layouts[ComposeC]},
  {"v", "V", 1.0, Code, KEY_V, &layouts[ComposeV]},
  {"b", "B", 1.0, Code, KEY_B, &layouts[ComposeB]},
  {"n", "N", 1.0, Code, KEY_N, &layouts[ComposeN]},
  {"é", "É", 1.0, Copy, 0x00E9, 0, 0x00C9},
  {"è", "È", 1.0, Copy, 0x00E8, 0, 0x00C8},
  {"⌫", "⌫", 1.0, Code, KEY_BACKSPACE, .scheme = 1},
  {"", "", 0.0, EndRow},

  {"⌨͕", "⌨͔", 1.0, NextLayer, .scheme = 1},
  {"à", "À", 1.0, Copy, 0x00E0, 0, 0x00C0},
  {"ç", "Ç", 1.0, Copy, 0x00E7, 0, 0x00C7},
  {",", "'", 1.0, Code, KEY_COMMA, &layouts[ComposeBracket]},
  {"", "Tab", 3.5, Code, KEY_SPACE},
  {".", "?", 1.0, Code, KEY_DOT, &layouts[ComposePunctuation]},
  {"Enter", "Enter", 1.5, Code, KEY_ENTER, .scheme = 1},

  /* end of layout */
  {"", "", 0.0, Last},
};
