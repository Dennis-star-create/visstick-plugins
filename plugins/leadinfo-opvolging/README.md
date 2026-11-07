# Leadinfo-opvolging

Een skill voor Claude die mails van Leadinfo Autopilot opvolgt:

Elke keer dat je de skill start, doet hij dit:

1. Zoekt in je verzonden mails de mails die Autopilot uit jouw naam verstuurde.
   Legt bedrijf, contactpersoon en e-mailadres vast.
2. Kijkt of je al iemand bij dat bedrijf kent uit eerder mailcontact. Zo ja,
   dan gaat de opvolging naar die persoon.
3. Leest de bezoekersrapportage van Leadinfo uit je mailbox (bedrijven en
   bezochte pagina's).
4. Schrijft per bedrijf een persoonlijke opvolgmail met als doel een afspraak.
5. Zet die mail als **concept** in je mailbox. Je leest hem na en verstuurt hem
   zelf. De skill verstuurt nooit iets.

## Nodig

- Claude Code (inbegrepen bij een Claude Pro-, Max- of Team-abonnement).
- Een koppeling met je mailbox die kan zoeken, lezen en **concepten maken**:
  - Gmail: de Gmail-connector in Claude (Instellingen → Connectors);
  - Outlook / Microsoft 365: een connector met conceptfunctie. Controleer dit
    bij de installatie; zonder conceptfunctie stopt de skill.
- Leadinfo Autopilot, gekoppeld aan je mailbox, en de e-mailmeldingen of
  rapportage van Leadinfo naar hetzelfde adres. Tip: zet jezelf in Autopilot
  in BCC (`autopilot_bcc: ja`), dan zoekt de skill sneller.

## Installeren

In Claude Code:

```
/plugin marketplace add Dennis-star-create/visstick-plugins
/plugin install leadinfo-opvolging@visstick
```

Start daarna één keer met de hand, in een gewoon gesprek:

```
claude "/leadinfo-opvolging"
```

De skill vraagt dan naar je instellingen (naam, handtekening, afspraaklink,
aanbod, uitsluitlijst) en schrijft ze naar `~/leadinfo-opvolging/instellingen.md`.
Het voorbeeld staat in `plugins/leadinfo-opvolging/skills/leadinfo-opvolging/instellingen-voorbeeld.md`.
Controleer de eerste concepten goed voordat je de planning aanzet.

## Twee keer per week automatisch

Na de installatie loopt er nog niets vanzelf: de skill doet alleen iets als
hij gestart wordt. Automatisch laten lopen stel je zelf in, zoals hieronder.

Plan de run op een dag nadat de Leadinfo-rapportage binnenkomt, bijvoorbeeld
dinsdag en vrijdag om 09:00. De computer moet dan aan staan.

**Mac (launchd).** Zet dit bestand in
`~/Library/LaunchAgents/ai.visstick.leadinfo-opvolging.plist` en laad het met
`launchctl load ~/Library/LaunchAgents/ai.visstick.leadinfo-opvolging.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>ai.visstick.leadinfo-opvolging</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string><string>-lc</string>
    <string>cd ~/leadinfo-opvolging &amp;&amp; claude -p "/leadinfo-opvolging" >> run.log 2>&amp;1</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
  </array>
</dict>
</plist>
```

Een run zonder scherm kan niet om toestemming vragen. Geef in
`~/leadinfo-opvolging/.claude/settings.json` alleen toegang tot wat de skill
nodig heeft: mail zoeken, lezen en concepten maken, en lezen en schrijven in de
werkmap. Geef geen toegang tot versturen.

De melding van elke run staat in `~/leadinfo-opvolging/run.log`. Het register
met alle contacten en hun status staat in `~/leadinfo-opvolging/register.csv`.

**Windows.** Gebruik Taakplanner met hetzelfde commando
(`claude -p "/leadinfo-opvolging"`), op dinsdag en vrijdag.

## Wat de skill nooit doet

- Mails versturen, beantwoorden, verwijderen of labelen.
- E-mailadressen raden.
- Leadinfo, tracking of bezochte pagina's noemen in de mail.
- Opvolgen bij wie heeft gereageerd, zich heeft afgemeld, onbestelbaar is,
  of met wie je al een lopend gesprek hebt.
