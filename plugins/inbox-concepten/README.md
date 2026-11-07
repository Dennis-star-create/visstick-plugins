# Inbox-concepten

Een skill voor Claude die je nieuwe mail doorloopt en antwoorden voor je klaarzet.

Elke keer dat je de skill start, doet hij dit:

1. Leest de mail die sinds de vorige keer binnenkwam.
2. Sorteert die: antwoord nodig, afspraak, zelf doen, ter info, automatisch.
3. Schrijft voor elke mail die een antwoord verdient een **concept** in jouw toon,
   in dezelfde mailthread. Wat hij niet weet, markeert hij met `[INVULLEN: …]`.
4. Geeft een kort overzicht: wat klaarstaat, wat je zelf moet doen, en wat ter
   info binnenkwam.

Je leest elk concept na en verstuurt het zelf. De skill verstuurt nooit iets.

## Nodig

- Claude met Claude Code (inbegrepen bij Claude Pro, Max of Team).
- Een koppeling met je mailbox die kan zoeken, lezen en **concepten maken**:
  - Gmail: de Gmail-connector in Claude (Instellingen → Connectors);
  - Outlook / Microsoft 365: een connector met conceptfunctie. Zonder
    conceptfunctie stopt de skill.

## Installeren

In Claude Code:

```
/plugin marketplace add Dennis-star-create/visstick-plugins
/plugin install inbox-concepten@visstick
```

## Eerste keer

Start één keer met de hand, in een gewoon gesprek:

```
claude "/inbox-concepten"
```

De skill vraagt naar je naam, handtekening, twee of drie voorbeeldmails (voor
de toon), vaste antwoorden en adressen die hij moet overslaan. Hij schrijft dat
naar `~/inbox-concepten/instellingen.md`. Het voorbeeld staat in
`plugins/inbox-concepten/skills/inbox-concepten/instellingen-voorbeeld.md`.

Lees de eerste concepten kritisch. Klopt de toon niet, voeg dan een betere
voorbeeldmail toe aan de instellingen.

## Elke ochtend automatisch

Na de installatie loopt er nog niets vanzelf. Wil je elke werkdag om 07:30 je
concepten klaar hebben staan, dan plan je dat zelf. De computer moet op dat
moment aan staan.

**Mac (launchd).** Zet dit bestand in
`~/Library/LaunchAgents/ai.visstick.inbox-concepten.plist` en laad het met
`launchctl load ~/Library/LaunchAgents/ai.visstick.inbox-concepten.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>ai.visstick.inbox-concepten</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string><string>-lc</string>
    <string>cd ~/inbox-concepten &amp;&amp; claude -p "/inbox-concepten" >> run.log 2>&amp;1</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>7</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>7</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>7</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>7</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>7</integer><key>Minute</key><integer>30</integer></dict>
  </array>
</dict>
</plist>
```

Een run zonder scherm kan niet om toestemming vragen. Geef in
`~/inbox-concepten/.claude/settings.json` alleen toegang tot wat de skill nodig
heeft: mail zoeken, lezen en concepten maken, en lezen en schrijven in de
werkmap. Geef geen toegang tot versturen of verwijderen.

Het overzicht van elke run staat in `~/inbox-concepten/overzicht-<datum>.md`.

**Windows.** Gebruik Taakplanner met hetzelfde commando
(`claude -p "/inbox-concepten"`), op werkdagen om 07:30.

## Wat de skill nooit doet

- Mails versturen, verwijderen, archiveren, labelen of op gelezen zetten.
- Links openen of bijlagen uitvoeren.
- Afspraken in je agenda zetten of accepteren.
- Feiten, prijzen of toezeggingen verzinnen.

Gevoelige mails (klachten, juridische zaken, onderhandelingen, sollicitaties)
krijgen geen concept. Die staan in het overzicht onder "Zelf doen".
