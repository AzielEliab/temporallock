import 'package:flutter/material.dart';

/// Paper and charcoal surfaces with an Aziel gold accent.
const Color kMatteBlack = Color(0xFF12110E);
const Color kSurface = Color(0xFF1C1A16);
const Color kGold = Color(0xFFC9A227);
const Color kOnGold = Color(0xFF1A1408);
const Color kIvory = Color(0xFFF4EFE6);
const Color kPaper = Color(0xFFF7F4EE);
const Color kInk = Color(0xFF1A1814);
const Color kLine = Color(0xFFE3D9C4);

ThemeData buildDarkTheme() {
  const scheme = ColorScheme.dark(
    brightness: Brightness.dark,
    primary: kGold,
    onPrimary: kOnGold,
    secondary: kGold,
    onSecondary: kOnGold,
    surface: kSurface,
    onSurface: kIvory,
    error: Color(0xFFFFB4AB),
    onError: kMatteBlack,
  );
  return _theme(scheme, kMatteBlack, kIvory);
}

ThemeData buildLightTheme() {
  const scheme = ColorScheme.light(
    brightness: Brightness.light,
    primary: kGold,
    onPrimary: kOnGold,
    secondary: kGold,
    onSecondary: kOnGold,
    surface: Color(0xFFFFFDF8),
    onSurface: kInk,
    error: Color(0xFF8D1D1D),
    onError: Color(0xFFFFFDF8),
  );
  return _theme(scheme, kPaper, kInk);
}

ThemeData buildAppTheme() => buildDarkTheme();

ThemeData _theme(ColorScheme scheme, Color scaffold, Color ink) {
  return ThemeData(
    useMaterial3: true,
    brightness: scheme.brightness,
    colorScheme: scheme,
    scaffoldBackgroundColor: scaffold,
    focusColor: kGold,
    hoverColor: const Color(0x33C9A227),
    splashColor: const Color(0x22C9A227),
    appBarTheme: AppBarTheme(
      backgroundColor: scaffold,
      foregroundColor: ink,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: scheme.surface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: scheme.brightness == Brightness.dark ? const Color(0x33C9A227) : kLine),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: scheme.brightness == Brightness.dark ? const Color(0xFF14120F) : Colors.white,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: kGold, width: 2),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: kGold,
        foregroundColor: kOnGold,
        minimumSize: const Size(64, 48),
        textStyle: const TextStyle(fontWeight: FontWeight.w700),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: ink,
        minimumSize: const Size(64, 48),
      ),
    ),
  );
}
