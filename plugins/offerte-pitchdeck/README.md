# Offerte-pitchdeck

Een skill voor Claude die van één klantgesprek in één keer een offerte en een
pitchdeck maakt.

## Wat het doet

1. Leest het gesprek: een transcript van Teams, Zoom of Meet, je aantekeningen,
   een mailwisseling of een document in Google Drive.
2. Haalt eruit wat telt: de situatie van de klant, wat hij wil bereiken, de
   aanpak in fases, de planning en wat je levert.
3. Prijst alleen met **je eigen prijslijst**. Staat iets er niet in, dan komt
   er `[INVULLEN]` te staan. Het script rekent subtotaal, btw en totaal zelf
   uit.
4. Maakt twee bestanden in jouw huisstijl (kleuren, lettertype, logo):
   - **offerte.docx**: met offertenummer, KvK- en btw-nummer, prijstabel,
     voorwaarden en een akkoordregel;
   - **pitchdeck.pptx**: 8 slides voor het vervolggesprek.
5. Zet, als je dat wilt, een korte begeleidende mail als **concept** klaar.

Jij leest alles na en verstuurt het zelf. De skill verstuurt nooit iets.

## Nodig

- Claude met Claude Code (inbegrepen bij Claude Pro, Max of Team).
- Python 3 met `python-docx` en `python-pptx`. De skill vraagt of hij die mag
  installeren (`python3 -m pip install --user python-docx python-pptx`).
- Het gesprek als bestand of geplakte tekst. Optioneel: de connector voor
  Google Drive, Gmail of Outlook (Instellingen → Connectors) om het gesprek daar
  op te halen en de mail als concept klaar te zetten.
- Optioneel: LibreOffice, waarmee de skill zijn eigen slides controleert.

## Installeren

In Claude Code:

```
/plugin marketplace add Dennis-star-create/visstick-plugins
/plugin install offerte-pitchdeck@visstick
```

## Eerste keer

Start in een gewoon gesprek:

```
claude "/offerte-pitchdeck"
```

De skill vraagt naar je bedrijfsgegevens, KvK- en btw-nummer, huisstijl en logo,
je prijslijst, standaardvoorwaarden en drie tot acht redenen waarom klanten
voor jou kiezen. Hij schrijft dat naar `~/offerte-pitchdeck/instellingen.md`.
Het voorbeeld staat in
`plugins/offerte-pitchdeck/skills/offerte-pitchdeck/instellingen-voorbeeld.md`.

Daarna bijvoorbeeld:

```
/offerte-pitchdeck maak een offerte van ~/Downloads/gesprek-bakkerij.txt
```

De bestanden komen in `~/offerte-pitchdeck/offertes/<datum>-<klant>/`.

Tip: hoe vollediger je prijslijst, hoe minder `[INVULLEN]`.

## Automatisch laten lopen

Deze skill draai je met de hand, direct na een gesprek. Hij heeft je controle
nodig: prijzen en toezeggingen gaan naar een klant. Plan hem dus niet
automatisch in.

## Wat de skill nooit doet

- Offertes of mails versturen.
- Prijzen, kortingen, levertijden of garanties verzinnen.
- Gegevens van de ene klant gebruiken in de offerte van een andere.
- Bestanden buiten `~/offerte-pitchdeck/` wijzigen of verwijderen.
