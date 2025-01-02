# Translation Guide

1. Open the `languages` folder in the repo. [Quick link on GitHub](languages/)
2. Choose a base language file to translate from. It could be whatever language you are familiar with.
3. Find the base language file in the `languages` folder and open it in a text editor.
   A random line from a language file will look like this:
   ```
   LangString WelcomeTitle ${LANG_ENGLISH} "Welcome to the Euro Truck Simulator 2 Lane Assist Installer"
   ```
   Let's take things apart:
   - `LangString` is a keyword that indicates that this line is a language string. Don't change it.
   - `WelcomeTitle` is the key of the string. Usually you don't have to change it.
   - `${LANG_ENGLISH}` is a identifier that indicates the language of the string. [Below](#available-languages) is a list of all available languages.
   - `"Welcome to the Euro Truck Simulator 2 Lane Assist Installer"` is the value of the string. This is what you need to translate.
   
   For example, here's a translated version of the `WelcomeTitle` string in Chinese:
   ```
   LangString WelcomeTitle ${LANG_SIMPCHINESE} "欢迎使用 欧卡2车道辅助 / ETS2LA 安装程序"
   ```

4. Choose a language to translate to. You can choose any language that is not the base language.
5. Create a file with the same name as the base language file, but with the language code of the language you are translating to. For example, if you are translating to German, create a file called `de.nsh` in the `languages` folder.
6. Open the new language file in a text editor and copy all the lines from the base language file that you want to translate.
7. Translate the copied lines to the new language. Make sure to keep the same structure of the `LangString` keyword and the key.
8. Save the new language file.
9.  Commit the changes to the repo, and open a Pull Request on GitHub.
10. Wait for a review from a maintainer. The maintainer will help modifying the main program to support the new language.
11. Once the changes are merged, CI will be triggered and a new release will be created. You can download the new release and test it to make sure everything is working as expected.

## Available Languages

**(extracted from NSIS 3.10)**

*Sortings may vary*

- `LANG_SERBIAN`: Serbian
- `LANG_VIETNAMESE`: Vietnamese
- `LANG_ASTURIAN`: Asturian
- `LANG_GREEK`: Greek
- `LANG_TURKISH`: Turkish
- `LANG_GEORGIAN`: Georgian
- `LANG_NORWEGIAN`: Norwegian
- `LANG_MACEDONIAN`: Macedonian
- `LANG_HEBREW`: Hebrew
- `LANG_BELARUSIAN`: Belarusian
- `LANG_PORTUGUESEBR`: PortugueseBR
- `LANG_WELSH`: Welsh
- `LANG_KOREAN`: Korean
- `LANG_JAPANESE`: Japanese
- `LANG_ESTONIAN`: Estonian
- `LANG_AFRIKAANS`: Afrikaans
- `LANG_SCOTSGAELIC`: ScotsGaelic
- `LANG_CZECH`: Czech
- `LANG_ESPERANTO`: Esperanto
- `LANG_KURDISH`: Kurdish
- `LANG_LITHUANIAN`: Lithuanian
- `LANG_LATVIAN`: Latvian
- `LANG_PASHTO`: Pashto
- `LANG_BOSNIAN`: Bosnian
- `LANG_CROATIAN`: Croatian
- `LANG_FRENCH`: French
- `LANG_FARSI`: Farsi
- `LANG_HINDI`: Hindi
- `LANG_HUNGARIAN`: Hungarian
- `LANG_SERBIANLATIN`: SerbianLatin
- `LANG_BULGARIAN`: Bulgarian
- `LANG_SIMPCHINESE`: SimpChinese
- `LANG_INDONESIAN`: Indonesian
- `LANG_SLOVENIAN`: Slovenian
- `LANG_ALBANIAN`: Albanian
- `LANG_ARABIC`: Arabic
- `LANG_ARMENIAN`: Armenian
- `LANG_UKRAINIAN`: Ukrainian
- `LANG_GERMAN`: German
- `LANG_CATALAN`: Catalan
- `LANG_MALAY`: Malay
- `LANG_SWEDISH`: Swedish
- `LANG_THAI`: Thai
- `LANG_PORTUGUESE`: Portuguese
- `LANG_ICELANDIC`: Icelandic
- `LANG_LUXEMBOURGISH`: Luxembourgish
- `LANG_IRISH`: Irish
- `LANG_TRADCHINESE`: TradChinese
- `LANG_UZBEK`: Uzbek
- `LANG_SPANISHINTERNATIONAL`: SpanishInternational
- `LANG_BASQUE`: Basque
- `LANG_POLISH`: Polish
- `LANG_NORWEGIANNYNORSK`: NorwegianNynorsk
- `LANG_TATAR`: Tatar
- `LANG_RUSSIAN`: Russian
- `LANG_FINNISH`: Finnish
- `LANG_BRETON`: Breton
- `LANG_GALICIAN`: Galician
- `LANG_MONGOLIAN`: Mongolian
- `LANG_DUTCH`: Dutch
- `LANG_SPANISH`: Spanish
- `LANG_ROMANIAN`: Romanian
- `LANG_ENGLISH`: English
- `LANG_ITALIAN`: Italian
- `LANG_DANISH`: Danish
- `LANG_SLOVAK`: Slovak
- `LANG_CORSICAN`: Corsican
